import json
import re
import sys
from typing import List, Dict, Any, Tuple, Optional
from ..schemas.contract import (
    DependenciesReport,
    EcosystemDependencies,
    DependencyItem,
    Evidence,
    AnalysisWarning,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # fallback for older versions if ever needed

# Regex for parsing pip requirements
# Extracts package name, extras, and version specifier
REQUIREMENT_REGEX = re.compile(
    r"^\s*([a-zA-Z0-9_\-\.]+)(?:\[([a-zA-Z0-9_\-,\s]+)\])?\s*([=><~^!].*)?$"
)

def parse_requirements_txt(
    content: str,
    manifest_path: str = "requirements.txt",
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> Tuple[List[DependencyItem], List[AnalysisWarning]]:
    """
    Parses requirements.txt lines handling comments, extras, markers,
    and flags (-r, -i, -e, --extra-index-url) without crashing.
    """
    items: List[DependencyItem] = []
    warnings: List[AnalysisWarning] = []
    github_url = f"{repo_html_url}/blob/{default_branch}/{manifest_path}"

    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        # Skip empty lines and comment lines
        if not line or line.startswith("#"):
            continue

        # Strip inline comments
        if " #" in line:
            line = line.split(" #", 1)[0].strip()

        # Handle pip flags (-r, -f, -i, --index-url, etc.)
        if line.startswith(("-", "--")):
            if line.startswith(("-r ", "-r\t")):
                sub_file = line.split(maxsplit=1)[1].strip()
                warnings.append(AnalysisWarning(
                    code="REQUIREMENTS_RECURSIVE_INCLUDE",
                    message=f"Line {line_no} includes sub-requirements file '{sub_file}', which was not evaluated."
                ))
            continue

        # Strip environment markers (e.g. ; python_version >= '3.8')
        marker = None
        if ";" in line:
            parts = line.split(";", 1)
            line = parts[0].strip()
            marker = parts[1].strip()

        # Handle editable / VCS installs (e.g. -e git+https://...)
        if "git+" in line or "http://" in line or "https://" in line:
            pkg_name = line.split("/")[-1].split(".git")[0].split("@")[0].strip()
            if pkg_name:
                items.append(DependencyItem(
                    name=pkg_name,
                    version_spec="vcs/direct",
                    evidence=Evidence(
                        path=manifest_path,
                        reason=f"Declared in {manifest_path} (line {line_no}) via VCS/URL",
                        github_url=f"{github_url}#L{line_no}"
                    )
                ))
            continue

        # Parse standard dependency
        match = REQUIREMENT_REGEX.match(line)
        if match:
            pkg_name, extras, version_spec = match.groups()
            spec_str = version_spec.strip() if version_spec else None
            if extras:
                spec_str = f"[{extras}] {spec_str}" if spec_str else f"[{extras}]"

            reason = f"Declared in manifest {manifest_path} on line {line_no}"
            if marker:
                reason += f" (marker: {marker})"

            items.append(DependencyItem(
                name=pkg_name,
                version_spec=spec_str,
                evidence=Evidence(
                    path=manifest_path,
                    reason=reason,
                    github_url=f"{github_url}#L{line_no}"
                )
            ))
        else:
            warnings.append(AnalysisWarning(
                code="REQUIREMENTS_UNPARSED_LINE",
                message=f"Could not parse dependency on line {line_no} in {manifest_path}: '{line}'"
            ))

    return items, warnings

def parse_package_json(
    content: str,
    manifest_path: str = "package.json",
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> Tuple[List[DependencyItem], List[DependencyItem], List[AnalysisWarning]]:
    """
    Parses package.json dependencies and devDependencies.
    Returns: (runtime_deps, dev_deps, warnings)
    """
    runtime_deps: List[DependencyItem] = []
    dev_deps: List[DependencyItem] = []
    warnings: List[AnalysisWarning] = []
    github_url = f"{repo_html_url}/blob/{default_branch}/{manifest_path}"

    try:
        data = json.loads(content)
    except Exception as e:
        warnings.append(AnalysisWarning(
            code="MALFORMED_PACKAGE_JSON",
            message=f"Failed to parse {manifest_path}: {str(e)}"
        ))
        return runtime_deps, dev_deps, warnings

    if not isinstance(data, dict):
        warnings.append(AnalysisWarning(
            code="INVALID_PACKAGE_JSON_SHAPE",
            message=f"{manifest_path} does not contain a JSON object."
        ))
        return runtime_deps, dev_deps, warnings

    # Runtime dependencies
    deps = data.get("dependencies")
    if isinstance(deps, dict):
        for name, spec in deps.items():
            runtime_deps.append(DependencyItem(
                name=name,
                version_spec=str(spec) if spec is not None else None,
                evidence=Evidence(
                    path=manifest_path,
                    reason=f"Declared under 'dependencies' in {manifest_path}",
                    github_url=github_url
                )
            ))

    # Dev dependencies
    devs = data.get("devDependencies")
    if isinstance(devs, dict):
        for name, spec in devs.items():
            dev_deps.append(DependencyItem(
                name=name,
                version_spec=str(spec) if spec is not None else None,
                evidence=Evidence(
                    path=manifest_path,
                    reason=f"Declared under 'devDependencies' in {manifest_path}",
                    github_url=github_url
                )
            ))

    return runtime_deps, dev_deps, warnings

def parse_pyproject_toml(
    content: str,
    manifest_path: str = "pyproject.toml",
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> Tuple[List[DependencyItem], List[DependencyItem], List[AnalysisWarning]]:
    """
    Parses pyproject.toml dependencies (PEP 621 and Poetry).
    Returns: (runtime_deps, dev_deps, warnings)
    """
    runtime_deps: List[DependencyItem] = []
    dev_deps: List[DependencyItem] = []
    warnings: List[AnalysisWarning] = []
    github_url = f"{repo_html_url}/blob/{default_branch}/{manifest_path}"

    try:
        data = tomllib.loads(content)
    except Exception as e:
        warnings.append(AnalysisWarning(
            code="MALFORMED_PYPROJECT_TOML",
            message=f"Failed to parse {manifest_path}: {str(e)}"
        ))
        return runtime_deps, dev_deps, warnings

    # 1. PEP 621: [project.dependencies]
    project = data.get("project")
    if isinstance(project, dict):
        pep_deps = project.get("dependencies")
        if isinstance(pep_deps, list):
            for dep_str in pep_deps:
                if isinstance(dep_str, str):
                    match = REQUIREMENT_REGEX.match(dep_str.strip())
                    if match:
                        name, extras, spec = match.groups()
                        spec_str = spec.strip() if spec else None
                        if extras:
                            spec_str = f"[{extras}] {spec_str}" if spec_str else f"[{extras}]"
                        runtime_deps.append(DependencyItem(
                            name=name,
                            version_spec=spec_str,
                            evidence=Evidence(
                                path=manifest_path,
                                reason=f"Declared under [project.dependencies] in {manifest_path}",
                                github_url=github_url
                            )
                        ))

        # [project.optional-dependencies] -> dev
        opt_deps = project.get("optional-dependencies")
        if isinstance(opt_deps, dict):
            for group, group_deps in opt_deps.items():
                if isinstance(group_deps, list):
                    for dep_str in group_deps:
                        if isinstance(dep_str, str):
                            match = REQUIREMENT_REGEX.match(dep_str.strip())
                            if match:
                                name, extras, spec = match.groups()
                                dev_deps.append(DependencyItem(
                                    name=name,
                                    version_spec=spec.strip() if spec else None,
                                    evidence=Evidence(
                                        path=manifest_path,
                                        reason=f"Declared under [project.optional-dependencies.{group}] in {manifest_path}",
                                        github_url=github_url
                                    )
                                ))

    # 2. Poetry: [tool.poetry.dependencies]
    tool_poetry = data.get("tool", {}).get("poetry", {})
    if isinstance(tool_poetry, dict):
        poetry_deps = tool_poetry.get("dependencies")
        if isinstance(poetry_deps, dict):
            for name, spec in poetry_deps.items():
                if name.lower() == "python":
                    continue  # python runtime requirement, not a library dependency
                spec_str = str(spec) if not isinstance(spec, dict) else str(spec.get("version"))
                runtime_deps.append(DependencyItem(
                    name=name,
                    version_spec=spec_str,
                    evidence=Evidence(
                        path=manifest_path,
                        reason=f"Declared under [tool.poetry.dependencies] in {manifest_path}",
                        github_url=github_url
                    )
                ))

        # Poetry dev dependencies
        dev_group = tool_poetry.get("group", {}).get("dev", {}).get("dependencies")
        legacy_dev = tool_poetry.get("dev-dependencies")
        all_devs = {}
        if isinstance(legacy_dev, dict):
            all_devs.update(legacy_dev)
        if isinstance(dev_group, dict):
            all_devs.update(dev_group)

        for name, spec in all_devs.items():
            spec_str = str(spec) if not isinstance(spec, dict) else str(spec.get("version"))
            dev_deps.append(DependencyItem(
                name=name,
                version_spec=spec_str,
                evidence=Evidence(
                    path=manifest_path,
                    reason=f"Declared under Poetry dev-dependencies in {manifest_path}",
                    github_url=github_url
                )
            ))

    return runtime_deps, dev_deps, warnings

def build_dependencies_report(
    manifest_contents: Dict[str, str],
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> Tuple[DependenciesReport, List[AnalysisWarning]]:
    """
    Coordinates dependency manifest parsers across all discovered manifest files.
    """
    ecosystems: List[EcosystemDependencies] = []
    all_warnings: List[AnalysisWarning] = []

    # Check for npm manifests
    for path, content in manifest_contents.items():
        if path == "package.json" or path.endswith("/package.json"):
            runtime, dev, warns = parse_package_json(
                content, manifest_path=path, repo_html_url=repo_html_url, default_branch=default_branch
            )
            all_warnings.extend(warns)
            ecosystems.append(EcosystemDependencies(
                ecosystem="npm",
                manifest_path=path,
                runtime=runtime,
                dev=dev
            ))

    # Check for Python manifests
    for path, content in manifest_contents.items():
        if path == "requirements.txt" or path.endswith("/requirements.txt"):
            runtime, warns = parse_requirements_txt(
                content, manifest_path=path, repo_html_url=repo_html_url, default_branch=default_branch
            )
            all_warnings.extend(warns)
            ecosystems.append(EcosystemDependencies(
                ecosystem="pip",
                manifest_path=path,
                runtime=runtime,
                dev=[]
            ))
        elif path == "pyproject.toml" or path.endswith("/pyproject.toml"):
            runtime, dev, warns = parse_pyproject_toml(
                content, manifest_path=path, repo_html_url=repo_html_url, default_branch=default_branch
            )
            all_warnings.extend(warns)
            ecosystems.append(EcosystemDependencies(
                ecosystem="poetry/pep621",
                manifest_path=path,
                runtime=runtime,
                dev=dev
            ))

    return DependenciesReport(ecosystems=ecosystems), all_warnings
