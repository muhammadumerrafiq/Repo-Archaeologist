from typing import List, Dict, Any, Optional
from ..schemas.contract import FileTreeNode, FileTreeReport, FileKind
from .rules import WELL_KNOWN_FILE_DESCRIPTIONS

SOURCE_EXTENSIONS = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".cs",
    ".rb", ".php", ".swift", ".kt", ".scala", ".lua", ".sh", ".bash",
    ".html", ".css", ".scss", ".sass", ".less", ".vue", ".svelte"
}

TEST_EXTENSIONS = {
    ".spec.ts", ".spec.js", ".spec.tsx", ".spec.jsx",
    ".test.ts", ".test.js", ".test.tsx", ".test.jsx",
    "_test.py", "test_.py", "_test.go"
}

CONFIG_FILENAMES = {
    "package.json", "tsconfig.json", "vite.config.ts", "vite.config.js",
    "next.config.js", "next.config.mjs", "next.config.ts",
    "tailwind.config.js", "tailwind.config.ts", "postcss.config.js",
    "eslint.config.js", ".eslintrc.json", ".eslintrc.js",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "pytest.ini", "setup.cfg", "pyproject.toml", "Makefile",
    ".gitignore", ".env.example", ".prettierrc"
}

DOCS_EXTENSIONS = {".md", ".rst", ".txt", ".adoc", ".pdf"}
ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".eot"}
DATA_EXTENSIONS = {".json", ".yaml", ".yml", ".xml", ".csv", ".tsv", ".sqlite", ".db"}
LOCKFILE_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock", "poetry.lock", "uv.lock", "Pipfile.lock"}

def classify_file_kind(path: str) -> FileKind:
    """Classifies a file path into standard archaeological file kinds."""
    filename = path.split("/")[-1].lower()

    # CI workflows
    if ".github/workflows/" in path or ".gitlab-ci" in path or ".circleci" in path:
        return "ci"

    # Lockfiles
    if filename in LOCKFILE_NAMES:
        return "lockfile"

    # Tests
    if any(path.lower().endswith(te) for te in TEST_EXTENSIONS) or "test_" in filename or "_test" in filename or "/tests/" in path or "/__tests__/" in path:
        return "test"

    # Documentation
    if filename == "license" or filename == "copying" or any(filename.endswith(ext) for ext in DOCS_EXTENSIONS) or "/docs/" in path:
        return "docs"

    # Build outputs
    if path.startswith(("dist/", "build/", "out/", ".next/", "target/")) or "/dist/" in path:
        return "build"

    # Known Configs
    if filename in CONFIG_FILENAMES or filename.startswith(".env") or filename.endswith(".config.js") or filename.endswith(".config.ts"):
        return "config"

    # Assets
    if any(filename.endswith(ext) for ext in ASSET_EXTENSIONS):
        return "asset"

    # Data files
    if any(filename.endswith(ext) for ext in DATA_EXTENSIONS):
        return "data"

    # Source code
    if any(filename.endswith(ext) for ext in SOURCE_EXTENSIONS):
        return "source"

    return "unknown"

def build_file_tree(
    raw_tree_nodes: List[Dict[str, Any]],
    is_truncated: bool = False,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main"
) -> FileTreeReport:
    """
    Builds structured file tree report from Git Tree API response.
    Each file node receives a file_kind classification and a description only if well-known.
    """
    nodes: List[FileTreeNode] = []

    for item in raw_tree_nodes:
        path = item.get("path", "")
        if not path:
            continue

        raw_type = item.get("type", "blob")
        node_type = "file" if raw_type == "blob" else "dir"
        size = item.get("size")

        filename = path.split("/")[-1]
        description = WELL_KNOWN_FILE_DESCRIPTIONS.get(filename) if node_type == "file" else None
        file_kind = classify_file_kind(path) if node_type == "file" else "unknown"

        if node_type == "file":
            github_url = f"{repo_html_url}/blob/{default_branch}/{path}"
        else:
            github_url = f"{repo_html_url}/tree/{default_branch}/{path}"

        nodes.append(FileTreeNode(
            path=path,
            type=node_type,
            size=size,
            file_kind=file_kind,
            description=description,
            github_url=github_url
        ))

    return FileTreeReport(nodes=nodes, truncated=is_truncated)
