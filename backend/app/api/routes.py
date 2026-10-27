import time
import base64
import logging
from typing import Dict, List, Set, Optional
from fastapi import APIRouter, HTTPException, status

from ..config import settings
from ..cache import analysis_cache
from ..schemas.contract import (
    HealthResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    RepoMeta,
    ReadmeReport,
    AnalysisWarning,
    AnalysisStats,
)
from ..github.url_parser import parse_github_url
from ..github.client import GitHubClient
from ..github.errors import (
    RateLimitExceededError,
    GitHubError,
)
from ..analysis import (
    analyze_languages,
    CatalogIdGenerator,
    detect_ecosystems,
    detect_package_managers,
    detect_frameworks_and_tools,
    detect_config_files,
    detect_entry_points,
    build_dependencies_report,
    build_file_tree,
    build_architecture_graph,
    generate_plain_english_guide,
)

router = APIRouter(prefix="/api")
logger = logging.getLogger("repo_archaeologist")

IGNORED_DIRECTORY_PREFIXES = (
    "node_modules/", "dist/", "build/", ".next/", "out/",
    "vendor/", ".git/", "__pycache__/", ".venv/", "venv/",
    ".pytest_cache/", ".tox/", "coverage/"
)

MANIFEST_FILENAMES = {
    "package.json", "requirements.txt", "pyproject.toml",
    "setup.py", "Pipfile", "go.mod", "Cargo.toml"
}

PRIORITY_ENTRY_FILES = {
    "main.py", "app.py", "server.js", "server.ts",
    "index.js", "index.ts", "src/main.tsx", "src/main.ts",
    "src/App.tsx", "src/App.jsx", "src/index.ts", "src/index.js",
    "Dockerfile", "docker-compose.yml"
}

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check and configuration status"
)
async def health_check():
    """
    Returns API health status and whether a GitHub token is configured.
    Never exposes the token, its prefix, or its length.
    """
    return HealthResponse(
        status="ok",
        github_token_configured=settings.is_token_configured
    )

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze a public GitHub repository"
)
async def analyze_repository(payload: AnalyzeRequest):
    """
    Deterministically analyzes a public GitHub repository.
    Enforces strict URL parsing, rate-limit safety, byte caps, and caching.
    """
    start_time = time.perf_counter()
    api_calls_made = 0
    warnings: List[AnalysisWarning] = []

    # 1. Parse and validate GitHub URL
    parsed_repo = parse_github_url(payload.url)
    owner = parsed_repo.owner
    repo = parsed_repo.name

    logger.info("Starting analysis for %s/%s", owner, repo)

    async with GitHubClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        # 2. Fetch repository metadata
        repo_data = await client.get_repo(owner, repo)
        api_calls_made += 1

        branch = repo_data.get("default_branch") or "main"
        pushed_at = repo_data.get("pushed_at") or ""
        cache_key = f"{parsed_repo.full_name}@{pushed_at or branch}"

        # Check Cache
        cached_res = analysis_cache.get(cache_key)
        if cached_res:
            logger.info("Serving analysis for %s from in-memory cache", cache_key)
            return cached_res

        # 3. Fetch languages breakdown
        api_langs = {}
        try:
            api_langs = await client.get_languages(owner, repo)
            api_calls_made += 1
        except Exception as e:
            warnings.append(AnalysisWarning(
                code="LANGUAGES_FETCH_FAILED",
                message=f"Could not fetch language metrics: {str(e)}"
            ))

        # 4. Fetch README
        readme_report = ReadmeReport(found=False)
        try:
            readme_data = await client.get_readme(owner, repo)
            api_calls_made += 1
            if readme_data:
                html_url = readme_data.get("html_url")
                raw_content = readme_data.get("content", "")
                excerpt = None
                if raw_content:
                    try:
                        decoded = base64.b64decode(raw_content).decode("utf-8", errors="replace")
                        # First 500 characters of clean text
                        excerpt = decoded.strip()[:500]
                    except Exception:
                        excerpt = None
                readme_report = ReadmeReport(
                    found=True,
                    excerpt=excerpt,
                    html_url=html_url
                )
        except Exception as e:
            warnings.append(AnalysisWarning(
                code="README_FETCH_FAILED",
                message=f"Could not fetch README metadata: {str(e)}"
            ))

        # 5. Fetch Git recursive tree
        tree_data = await client.get_tree(owner, repo, branch)
        api_calls_made += 1

        is_tree_truncated = bool(tree_data.get("truncated", False))
        if is_tree_truncated:
            warnings.append(AnalysisWarning(
                code="TREE_TRUNCATED",
                message="Repository tree was truncated by GitHub API. Analysis covers returned subset."
            ))

        raw_tree_nodes = tree_data.get("tree", [])
        all_tree_files: Set[str] = set()
        candidates_to_fetch: List[str] = []

        # Filter out vendored/build directories and classify fetch candidates
        for node in raw_tree_nodes:
            path = node.get("path", "")
            node_type = node.get("type", "blob")
            if node_type == "blob" and path:
                all_tree_files.add(path)
                # Skip blacklisted directories
                if not any(path.startswith(prefix) for prefix in IGNORED_DIRECTORY_PREFIXES):
                    candidates_to_fetch.append(path)

        # 6. Prioritize files according to Section 5
        def file_priority(p: str) -> int:
            filename = p.split("/")[-1]
            if filename in MANIFEST_FILENAMES:
                return 100
            if filename in PRIORITY_ENTRY_FILES or p in PRIORITY_ENTRY_FILES:
                return 80
            if "/" not in p and (p.endswith(".json") or p.endswith(".ts") or p.endswith(".py")):
                return 60
            if p.startswith("src/") and (p.endswith(".ts") or p.endswith(".tsx") or p.endswith(".py") or p.endswith(".js")):
                return 40
            return 10

        sorted_candidates = sorted(candidates_to_fetch, key=file_priority, reverse=True)
        files_to_fetch = sorted_candidates[:settings.MAX_FILES_TO_FETCH]

        # 7. Fetch budgeted files
        fetched_contents: Dict[str, str] = {}
        manifest_contents: Dict[str, str] = {}
        total_bytes_fetched = 0

        for path in files_to_fetch:
            if total_bytes_fetched >= settings.MAX_TOTAL_BYTES:
                warnings.append(AnalysisWarning(
                    code="TOTAL_BYTE_BUDGET_REACHED",
                    message=f"Cumulative raw file budget ({settings.MAX_TOTAL_BYTES // (1024 * 1024)} MB) reached. Remaining files skipped."
                ))
                break

            try:
                content, was_truncated = await client.fetch_raw_file(
                    owner, repo, branch, path, max_bytes=settings.MAX_BYTES_PER_FILE
                )
                if was_truncated:
                    warnings.append(AnalysisWarning(
                        code="FILE_OVERSIZED",
                        message=f"Skipped '{path}': exceeds per-file size cap ({settings.MAX_BYTES_PER_FILE // 1024} KB)."
                    ))
                    continue

                if content is not None:
                    total_bytes_fetched += len(content.encode("utf-8"))
                    fetched_contents[path] = content
                    filename = path.split("/")[-1]
                    if filename in MANIFEST_FILENAMES:
                        manifest_contents[path] = content

            except RateLimitExceededError as rle:
                # If rate limited during raw file fetches, preserve partial results
                warnings.append(AnalysisWarning(
                    code="RATE_LIMITED_PARTIAL",
                    message=f"GitHub rate limit reached during analysis. Partial results returned. {rle.message}"
                ))
                break
            except Exception as e:
                warnings.append(AnalysisWarning(
                    code="FILE_FETCH_ERROR",
                    message=f"Could not fetch '{path}': {str(e)}"
                ))

    # 8. Run Analysis Engine (pure functions)
    languages = analyze_languages(api_languages=api_langs, tree_nodes=raw_tree_nodes)
    repo_html_url = repo_data.get("html_url") or f"https://github.com/{owner}/{repo}"

    # Dependencies
    dependencies_report, dep_warnings = build_dependencies_report(
        manifest_contents, repo_html_url=repo_html_url, default_branch=branch
    )
    warnings.extend(dep_warnings)

    id_gen = CatalogIdGenerator()

    # Detectors
    ecosystems = detect_ecosystems(all_tree_files, id_gen, repo_html_url, branch)
    package_managers = detect_package_managers(all_tree_files, id_gen, repo_html_url, branch)

    # Collect all declared dependencies across parsed manifests
    all_declared_deps: Set[str] = set()
    dep_manifest_map: Dict[str, str] = {}
    for eco in dependencies_report.ecosystems:
        for item in eco.runtime + eco.dev:
            all_declared_deps.add(item.name)
            dep_manifest_map[item.name] = eco.manifest_path

    frameworks = detect_frameworks_and_tools(
        all_declared_deps, dep_manifest_map, id_gen, repo_html_url, branch
    )

    tech_stack = ecosystems + package_managers + frameworks
    config_findings = detect_config_files(all_tree_files, id_gen, repo_html_url, branch)

    # Entry points
    entry_findings = detect_entry_points(
        all_tree_files, manifest_contents, fetched_contents, id_gen, repo_html_url, branch
    )

    # File Tree
    file_tree = build_file_tree(raw_tree_nodes, is_truncated=is_tree_truncated, repo_html_url=repo_html_url, default_branch=branch)

    # Architecture Graph
    entry_paths = {f.evidence[0].path for f in entry_findings if f.evidence}
    config_paths = {f.evidence[0].path for f in config_findings if f.evidence}

    graph_report, graph_warnings = build_architecture_graph(
        file_contents=fetched_contents,
        all_tree_files=all_tree_files,
        entry_point_paths=entry_paths,
        config_paths=config_paths,
        dependencies_report=dependencies_report,
        repo_html_url=repo_html_url,
        default_branch=branch
    )
    warnings.extend(graph_warnings)

    # Plain-English Guide
    guide = generate_plain_english_guide(
        repo_meta=RepoMeta(
            owner=owner,
            name=repo,
            full_name=parsed_repo.full_name,
            description=repo_data.get("description"),
            html_url=repo_html_url,
            default_branch=branch,
            stars=repo_data.get("stargazers_count", 0),
            forks=repo_data.get("forks_count", 0),
            open_issues=repo_data.get("open_issues_count", 0),
            license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            primary_language=repo_data.get("language"),
            topics=repo_data.get("topics", []),
            size_kb=repo_data.get("size", 0),
            pushed_at=repo_data.get("pushed_at"),
            archived=bool(repo_data.get("archived", False))
        ),
        languages=languages,
        tech_stack=tech_stack,
        config_files=config_findings,
        entry_points=entry_findings,
        dependencies_ecosystems=[eco.ecosystem for eco in dependencies_report.ecosystems]
    )

    analysis_ms = int((time.perf_counter() - start_time) * 1000)

    response = AnalyzeResponse(
        repo=RepoMeta(
            owner=owner,
            name=repo,
            full_name=parsed_repo.full_name,
            description=repo_data.get("description"),
            html_url=repo_html_url,
            default_branch=branch,
            stars=repo_data.get("stargazers_count", 0),
            forks=repo_data.get("forks_count", 0),
            open_issues=repo_data.get("open_issues_count", 0),
            license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            primary_language=repo_data.get("language"),
            topics=repo_data.get("topics", []),
            size_kb=repo_data.get("size", 0),
            pushed_at=repo_data.get("pushed_at"),
            archived=bool(repo_data.get("archived", False))
        ),
        languages=languages,
        tech_stack=tech_stack,
        config_files=config_findings,
        entry_points=entry_findings,
        dependencies=dependencies_report,
        file_tree=file_tree,
        graph=graph_report,
        guide=guide,
        readme=readme_report,
        warnings=warnings,
        stats=AnalysisStats(
            files_in_tree=len(all_tree_files),
            files_fetched=len(fetched_contents),
            api_calls_made=api_calls_made,
            analysis_ms=analysis_ms
        )
    )

    # Save in cache
    analysis_cache.set(cache_key, response)

    return response
