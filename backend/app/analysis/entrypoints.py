import json
import ast
import re
from typing import List, Dict, Set, Optional
from ..schemas.contract import Finding, Evidence
from .detectors import CatalogIdGenerator
from .rules import HEURISTIC_ENTRY_FILES

def detect_entry_points(
    file_paths: Set[str],
    manifest_contents: Dict[str, str],
    file_contents: Dict[str, str],
    id_gen: CatalogIdGenerator,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> List[Finding]:
    """
    Detects entry point candidates.
    Every finding is labeled as an entry point candidate.
    Confirmed: Explicitly declared in manifests (main, bin, scripts, Dockerfile CMD).
    Heuristic: Inferred from convention and standard file locations.
    """
    findings: List[Finding] = []
    seen_paths: Set[str] = set()

    # 1. Manifest declared: package.json (main, module, bin, scripts.start)
    for path, content in manifest_contents.items():
        if path == "package.json" or path.endswith("/package.json"):
            try:
                pkg_data = json.loads(content)
                github_url = f"{repo_html_url}/blob/{default_branch}/{path}"

                # 'main' or 'module' target
                for key in ("main", "module"):
                    target = pkg_data.get(key)
                    if target and isinstance(target, str):
                        findings.append(Finding(
                            id=id_gen.next_id(),
                            label=f"Package Entry Candidate ({key})",
                            category="Entry Point",
                            confidence="confirmed",
                            summary=f"Declared '{key}' entry point candidate in {path}: '{target}'",
                            evidence=[Evidence(
                                path=path,
                                reason=f"Explicitly declared '{key}: {target}' in {path}",
                                github_url=github_url
                            )]
                        ))
                        seen_paths.add(target.lstrip("./"))

                # 'bin' target(s)
                bin_field = pkg_data.get("bin")
                if isinstance(bin_field, str):
                    findings.append(Finding(
                        id=id_gen.next_id(),
                        label="CLI Binary Entry Candidate",
                        category="Entry Point",
                        confidence="confirmed",
                        summary=f"Declared executable CLI binary candidate in {path}: '{bin_field}'",
                        evidence=[Evidence(
                            path=path,
                            reason=f"Explicitly declared 'bin: {bin_field}' in {path}",
                            github_url=github_url
                        )]
                    ))
                    seen_paths.add(bin_field.lstrip("./"))
                elif isinstance(bin_field, dict):
                    for bin_name, bin_path in bin_field.items():
                        findings.append(Finding(
                            id=id_gen.next_id(),
                            label=f"CLI Binary Entry Candidate ({bin_name})",
                            category="Entry Point",
                            confidence="confirmed",
                            summary=f"Declared executable CLI command '{bin_name}' -> '{bin_path}' in {path}",
                            evidence=[Evidence(
                                path=path,
                                reason=f"Explicitly declared 'bin.{bin_name}: {bin_path}' in {path}",
                                github_url=github_url
                            )]
                        ))
                        seen_paths.add(str(bin_path).lstrip("./"))

                # 'scripts.start' or 'scripts.dev'
                scripts = pkg_data.get("scripts")
                if isinstance(scripts, dict):
                    for script_name in ("start", "dev"):
                        cmd = scripts.get(script_name)
                        if cmd and isinstance(cmd, str):
                            findings.append(Finding(
                                id=id_gen.next_id(),
                                label=f"Script Runner Candidate (npm run {script_name})",
                                category="Entry Point",
                                confidence="confirmed",
                                summary=f"npm run script '{script_name}': '{cmd}'",
                                evidence=[Evidence(
                                    path=path,
                                    reason=f"Declared 'scripts.{script_name}: {cmd}' in {path}",
                                    github_url=github_url
                                )]
                            ))
            except Exception:
                pass

    # 2. Manifest declared: Dockerfile CMD / ENTRYPOINT
    for path, content in file_contents.items():
        if path == "Dockerfile" or path.endswith("/Dockerfile"):
            github_url = f"{repo_html_url}/blob/{default_branch}/{path}"
            for line_no, raw_line in enumerate(content.splitlines(), start=1):
                line = raw_line.strip()
                if line.upper().startswith(("CMD ", "ENTRYPOINT ")):
                    cmd_type = "ENTRYPOINT" if line.upper().startswith("ENTRYPOINT") else "CMD"
                    cmd_val = line[len(cmd_type):].strip()
                    findings.append(Finding(
                        id=id_gen.next_id(),
                        label=f"Container {cmd_type} Entry Candidate",
                        category="Entry Point",
                        confidence="confirmed",
                        summary=f"Container execution instruction declared in Dockerfile line {line_no}",
                        evidence=[Evidence(
                            path=path,
                            reason=f"Declared '{line}' in {path} on line {line_no}",
                            github_url=f"{github_url}#L{line_no}"
                        )]
                    ))

    # 3. Code inspection: Python __name__ == '__main__' guard
    for path, content in file_contents.items():
        if path.endswith(".py"):
            try:
                tree = ast.parse(content)
                has_main_guard = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.If):
                        test = node.test
                        if isinstance(test, ast.Compare):
                            # Check for __name__ == '__main__' or '__main__' == __name__
                            left = getattr(test.left, "id", None)
                            comp_vals = [
                                getattr(comp, "value", None) or getattr(comp, "s", None)
                                for comp in test.comparators
                            ]
                            if left == "__name__" and "__main__" in comp_vals:
                                has_main_guard = True
                                break
                if has_main_guard:
                    findings.append(Finding(
                        id=id_gen.next_id(),
                        label="Python Executable Guard Candidate",
                        category="Entry Point",
                        confidence="confirmed",
                        summary=f"File contains '__name__ == \"__main__\"' guard candidate: '{path}'",
                        evidence=[Evidence(
                            path=path,
                            reason=(
                                "Confirmed '__name__ == \"__main__\"' block in file AST. "
                                "Indicates direct execution capability, candidate entry point."
                            ),
                            github_url=f"{repo_html_url}/blob/{default_branch}/{path}"
                        )]
                    ))
                    seen_paths.add(path)
            except Exception:
                pass

    # 4. Heuristic entry candidates from conventional file naming
    for rule in HEURISTIC_ENTRY_FILES:
        target_path = rule["path"]
        if target_path in file_paths and target_path not in seen_paths:
            findings.append(Finding(
                id=id_gen.next_id(),
                label="Application Entry Candidate",
                category="Entry Point",
                confidence="heuristic",
                summary=f"Likely entry point candidate by naming convention: '{target_path}'",
                evidence=[Evidence(
                    path=target_path,
                    reason=f"{rule['reason']}; inferred from standard project structure",
                    github_url=f"{repo_html_url}/blob/{default_branch}/{target_path}"
                )]
            ))
            seen_paths.add(target_path)

    # 5. Next.js pages/ or app/ router directory heuristics
    if any(fp.startswith("pages/") or fp.startswith("src/pages/") for fp in file_paths):
        findings.append(Finding(
            id=id_gen.next_id(),
            label="Next.js Pages Router Candidate",
            category="Entry Point",
            confidence="heuristic",
            summary="Next.js file-based page routing directory detected",
            evidence=[Evidence(
                path="pages/",
                reason="Standard Next.js pages/ router directory structure present",
                github_url=f"{repo_html_url}/tree/{default_branch}/pages"
            )]
        ))
    elif any(fp.startswith("app/") or fp.startswith("src/app/") for fp in file_paths):
        findings.append(Finding(
            id=id_gen.next_id(),
            label="Next.js App Router Candidate",
            category="Entry Point",
            confidence="heuristic",
            summary="Next.js App router directory detected",
            evidence=[Evidence(
                path="app/",
                reason="Standard Next.js app/ directory structure present",
                github_url=f"{repo_html_url}/tree/{default_branch}/app"
            )]
        ))

    return findings
