from typing import Dict, List, Optional
from ..schemas.contract import LanguageBreakdown

EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sh": "Shell",
    ".bash": "Shell",
    ".ps1": "PowerShell",
    ".md": "Markdown",
    ".sql": "SQL",
}

def analyze_languages(
    api_languages: Optional[Dict[str, int]] = None,
    tree_nodes: Optional[List[Dict[str, any]]] = None
) -> List[LanguageBreakdown]:
    """
    Analyzes language distribution.
    Primary: Confirmed byte values from GitHub API /languages endpoint.
    Fallback: Heuristic file extension aggregation if API returned no language bytes.
    """
    results: List[LanguageBreakdown] = []

    # 1. Primary: Use API language bytes if present and non-empty
    if api_languages and any(api_languages.values()):
        total_bytes = sum(api_languages.values())
        if total_bytes > 0:
            for lang, byte_count in sorted(api_languages.items(), key=lambda x: x[1], reverse=True):
                percent = round((byte_count / total_bytes) * 100.0, 1)
                results.append(
                    LanguageBreakdown(
                        name=lang,
                        bytes=byte_count,
                        percent=percent
                    )
                )
            return results

    # 2. Fallback: Extension-based heuristic from tree nodes
    if tree_nodes:
        lang_bytes: Dict[str, int] = {}
        for node in tree_nodes:
            if node.get("type") in ("blob", "file"):
                path = node.get("path", "")
                size = node.get("size") or 100 # default weight if size missing
                # Find extension
                dot_idx = path.rfind(".")
                if dot_idx != -1:
                    ext = path[dot_idx:].lower()
                    lang = EXTENSION_LANGUAGE_MAP.get(ext)
                    if lang and lang not in ("JSON", "YAML", "Markdown"):
                        lang_bytes[lang] = lang_bytes.get(lang, 0) + size

        total_bytes = sum(lang_bytes.values())
        if total_bytes > 0:
            for lang, byte_count in sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True):
                percent = round((byte_count / total_bytes) * 100.0, 1)
                results.append(
                    LanguageBreakdown(
                        name=lang,
                        bytes=byte_count,
                        percent=percent
                    )
                )

    return results
