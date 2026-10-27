from typing import List, Dict, Set, Any
from ..schemas.contract import Finding, Evidence
from .rules import (
    ECOSYSTEM_RULES,
    PACKAGE_MANAGER_RULES,
    FRAMEWORK_DEPENDENCY_RULES,
    CONFIG_FILE_RULES,
)

class CatalogIdGenerator:
    """Generates sequential catalog IDs e.g. ART-001, ART-002."""
    def __init__(self, start: int = 1):
        self._current = start

    def next_id(self) -> str:
        res = f"ART-{self._current:03d}"
        self._current += 1
        return res

def detect_ecosystems(
    file_paths: Set[str],
    id_gen: CatalogIdGenerator,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> List[Finding]:
    """Detects primary repository ecosystems based on marker files."""
    findings: List[Finding] = []

    for rule in ECOSYSTEM_RULES:
        found_markers = [m for m in rule["marker_files"] if m in file_paths]
        if found_markers:
            evidence_list = [
                Evidence(
                    path=m,
                    reason=f"Repository contains {m} manifest",
                    github_url=f"{repo_html_url}/blob/{default_branch}/{m}"
                )
                for m in found_markers
            ]
            findings.append(Finding(
                id=id_gen.next_id(),
                label=rule["name"],
                category=rule["category"],
                confidence=rule["confidence"],
                summary=f"Ecosystem confirmed by presence of {', '.join(found_markers)}",
                evidence=evidence_list
            ))

    return findings

def detect_package_managers(
    file_paths: Set[str],
    id_gen: CatalogIdGenerator,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> List[Finding]:
    """Detects active package managers based on lockfiles."""
    findings: List[Finding] = []

    for rule in PACKAGE_MANAGER_RULES:
        lockfiles = rule.get("lockfiles") or ([rule["lockfile"]] if "lockfile" in rule else [])
        present = [f for f in lockfiles if f in file_paths]
        if present:
            evidence_list = [
                Evidence(
                    path=lf,
                    reason=f"Repository contains {lf} lockfile",
                    github_url=f"{repo_html_url}/blob/{default_branch}/{lf}"
                )
                for lf in present
            ]
            findings.append(Finding(
                id=id_gen.next_id(),
                label=rule["name"],
                category=rule["category"],
                confidence=rule["confidence"],
                summary=f"Package manager confirmed by lockfile ({', '.join(present)})",
                evidence=evidence_list
            ))

    return findings

def detect_frameworks_and_tools(
    declared_dependencies: Set[str],
    dep_manifest_map: Dict[str, str],
    id_gen: CatalogIdGenerator,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> List[Finding]:
    """
    Detects frameworks, libraries, and tools declared in manifests (confirmed).
    """
    findings: List[Finding] = []
    seen_labels: Set[str] = set()

    # Lowercase dependency names for case-insensitive matching
    dep_lookup = {d.lower(): d for d in declared_dependencies}

    for rule in FRAMEWORK_DEPENDENCY_RULES:
        dep_key = rule["dep"].lower()
        if dep_key in dep_lookup:
            actual_name = dep_lookup[dep_key]
            if rule["name"] in seen_labels:
                continue
            seen_labels.add(rule["name"])

            manifest_path = dep_manifest_map.get(actual_name, "manifest")
            findings.append(Finding(
                id=id_gen.next_id(),
                label=rule["name"],
                category=rule["category"],
                confidence="confirmed",
                summary=rule["summary"],
                evidence=[
                    Evidence(
                        path=manifest_path,
                        reason=f"Declared in manifest '{manifest_path}' as '{actual_name}'",
                        github_url=f"{repo_html_url}/blob/{default_branch}/{manifest_path}"
                    )
                ]
            ))

    return findings

def detect_config_files(
    file_paths: Set[str],
    id_gen: CatalogIdGenerator,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> List[Finding]:
    """Detects configuration and tooling files in the repository tree."""
    findings: List[Finding] = []
    seen_labels: Set[str] = set()

    for rule in CONFIG_FILE_RULES:
        matching_files = []
        if "filename" in rule:
            if rule["filename"] in file_paths:
                matching_files.append(rule["filename"])
        elif "pattern" in rule:
            pat = rule["pattern"]
            for fp in file_paths:
                if pat in fp or fp.startswith(pat):
                    matching_files.append(fp)

        if matching_files and rule["name"] not in seen_labels:
            seen_labels.add(rule["name"])
            evidence_list = [
                Evidence(
                    path=mf,
                    reason=f"Configuration file present at '{mf}'",
                    github_url=f"{repo_html_url}/blob/{default_branch}/{mf}"
                )
                for mf in matching_files[:5] # cap evidence items per rule
            ]
            findings.append(Finding(
                id=id_gen.next_id(),
                label=rule["name"],
                category="Configuration",
                confidence="confirmed",
                summary=rule["summary"],
                evidence=evidence_list
            ))

    return findings
