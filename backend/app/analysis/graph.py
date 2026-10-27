import ast
import re
import posixpath
from typing import Dict, List, Set, Tuple, Optional
from ..schemas.contract import (
    GraphReport,
    GraphNode,
    GraphEdge,
    Evidence,
    NodeRole,
    EdgeType,
    Confidence,
    AnalysisWarning,
    DependenciesReport,
)
from .detectors import CatalogIdGenerator

# Regex for JS/TS import extraction
JS_TS_IMPORT_REGEX = re.compile(
    r"""(?:import\s+(?:[\w*\s{},]*\s+from\s+)?['"]([^'"]+)['"]|"""
    r"""export\s+(?:[\w*\s{},]*\s+from\s+)?['"]([^'"]+)['"]|"""
    r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)|"""
    r"""import\s*\(\s*['"]([^'"]+)['"]\s*\))"""
)

def _resolve_relative_path(
    source_file_path: str,
    import_spec: str,
    all_tree_files: Set[str]
) -> Optional[str]:
    """
    Resolves relative import specifiers (e.g. './utils', '../core')
    to an actual file path existing in all_tree_files.
    """
    if not import_spec.startswith((".", "/")):
        return None

    source_dir = posixpath.dirname(source_file_path)
    base_resolved = posixpath.normpath(posixpath.join(source_dir, import_spec))

    # Exact match
    if base_resolved in all_tree_files:
        return base_resolved

    # Try common extensions
    for ext in (".ts", ".tsx", ".js", ".jsx", ".py", ".mjs", ".cjs"):
        candidate = base_resolved + ext
        if candidate in all_tree_files:
            return candidate

    # Try index files inside directory
    for index_ext in ("/index.ts", "/index.tsx", "/index.js", "/index.jsx", "/__init__.py"):
        candidate = base_resolved + index_ext
        if candidate in all_tree_files:
            return candidate

    return None

def extract_python_imports(
    source_path: str,
    content: str,
    all_tree_files: Set[str]
) -> Tuple[List[str], Optional[AnalysisWarning]]:
    """
    Parses Python source using the standard ast module to extract confirmed imports.
    """
    resolved_targets: List[str] = []
    warning: Optional[AnalysisWarning] = None

    try:
        tree = ast.parse(content, filename=source_path)
    except SyntaxError as e:
        return resolved_targets, AnalysisWarning(
            code="PYTHON_AST_SYNTAX_ERROR",
            message=f"Syntax error parsing {source_path}: line {e.lineno}"
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_name = alias.name
                # Check if matches top-level file or package in repo
                py_candidate = mod_name.replace(".", "/") + ".py"
                init_candidate = mod_name.replace(".", "/") + "/__init__.py"
                if py_candidate in all_tree_files:
                    resolved_targets.append(py_candidate)
                elif init_candidate in all_tree_files:
                    resolved_targets.append(init_candidate)

        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            level = node.level # 0 = absolute, 1 = current dir, 2 = parent dir, etc.

            if level > 0:
                # Relative import
                source_dir = posixpath.dirname(source_path)
                for _ in range(level - 1):
                    source_dir = posixpath.dirname(source_dir)

                target_base = posixpath.normpath(posixpath.join(source_dir, mod.replace(".", "/"))) if mod else source_dir

                # Check module or package
                if target_base + ".py" in all_tree_files:
                    resolved_targets.append(target_base + ".py")
                elif target_base + "/__init__.py" in all_tree_files:
                    resolved_targets.append(target_base + "/__init__.py")
                else:
                    # Check individual names imported
                    for name in node.names:
                        sub_file = posixpath.normpath(posixpath.join(target_base, name.name + ".py"))
                        sub_pkg = posixpath.normpath(posixpath.join(target_base, name.name + "/__init__.py"))
                        if sub_file in all_tree_files:
                            resolved_targets.append(sub_file)
                        elif sub_pkg in all_tree_files:
                            resolved_targets.append(sub_pkg)
            else:
                # Absolute import inside repository
                target_path = mod.replace(".", "/")
                if target_path + ".py" in all_tree_files:
                    resolved_targets.append(target_path + ".py")
                elif target_path + "/__init__.py" in all_tree_files:
                    resolved_targets.append(target_path + "/__init__.py")

    return list(dict.fromkeys(resolved_targets)), warning

def extract_js_ts_imports(
    source_path: str,
    content: str,
    all_tree_files: Set[str]
) -> List[str]:
    """
    Lightweight parsing of JS/TS import/require/export specifiers.
    Resolves relative imports to files present in repository tree.
    """
    resolved_targets: List[str] = []

    for match in JS_TS_IMPORT_REGEX.finditer(content):
        # find non-empty capture group
        spec = next((g for g in match.groups() if g is not None), None)
        if not spec:
            continue

        resolved = _resolve_relative_path(source_path, spec, all_tree_files)
        if resolved:
            resolved_targets.append(resolved)

    return list(dict.fromkeys(resolved_targets))

def build_architecture_graph(
    file_contents: Dict[str, str],
    all_tree_files: Set[str],
    entry_point_paths: Set[str],
    config_paths: Set[str],
    dependencies_report: Optional[DependenciesReport] = None,
    repo_html_url: str = "https://github.com/owner/repo",
    default_branch: str = "main",
    max_nodes: int = 150
) -> Tuple[GraphReport, List[AnalysisWarning]]:
    """
    Builds the directed architecture graph:
    - Nodes: files with roles (entry, source, config, test, docs, dependency_group)
    - Edges:
      1. 'import' (solid): parsed code import resolved to repo file
      2. 'config' (dashed): config file referencing entry/source file
      3. 'dependency' (dotted): manifest to dependency group ('declared, not proven used')
    Caps at max_nodes (150) setting capped=True when exceeded.
    """
    nodes_map: Dict[str, GraphNode] = {}
    edges_list: List[GraphEdge] = []
    warnings: List[AnalysisWarning] = []
    seen_edges: Set[Tuple[str, str, str]] = set()

    def get_role(path: str) -> NodeRole:
        if path in entry_point_paths:
            return "entry"
        if path in config_paths or path.endswith((".json", ".toml", ".yml", ".yaml", ".ini", "Dockerfile", "Makefile")):
            return "config"
        if "test" in path.lower():
            return "test"
        if path.endswith((".md", ".txt", ".rst")):
            return "docs"
        if path.startswith("deps:"):
            return "dependency_group"
        return "source"

    def add_node(node_id: str, file_path: str, role: NodeRole, confidence: Confidence, reason: str):
        if node_id not in nodes_map:
            github_url = f"{repo_html_url}/blob/{default_branch}/{file_path}" if not node_id.startswith("deps:") else repo_html_url
            nodes_map[node_id] = GraphNode(
                id=node_id,
                path=file_path,
                role=role,
                confidence=confidence,
                evidence=[Evidence(
                    path=file_path,
                    reason=reason,
                    github_url=github_url
                )]
            )

    # 1. Parse imports from fetched files
    for path, content in file_contents.items():
        if path.endswith(".py"):
            targets, warn = extract_python_imports(path, content, all_tree_files)
            if warn:
                warnings.append(warn)
            for tgt in targets:
                add_node(path, path, get_role(path), "confirmed", "Source file present in repository")
                add_node(tgt, tgt, get_role(tgt), "confirmed", "Import target file resolved in repository tree")
                edge_key = (path, tgt, "import")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append(GraphEdge(
                        source=path,
                        target=tgt,
                        type="import",
                        confidence="confirmed",
                        evidence=[Evidence(
                            path=path,
                            reason=f"Parsed import in '{path}' resolving to '{tgt}'",
                            github_url=f"{repo_html_url}/blob/{default_branch}/{path}"
                        )]
                    ))

        elif path.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
            targets = extract_js_ts_imports(path, content, all_tree_files)
            for tgt in targets:
                add_node(path, path, get_role(path), "confirmed", "Source file present in repository")
                add_node(tgt, tgt, get_role(tgt), "confirmed", "Import target file resolved in repository tree")
                edge_key = (path, tgt, "import")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append(GraphEdge(
                        source=path,
                        target=tgt,
                        type="import",
                        confidence="confirmed",
                        evidence=[Evidence(
                            path=path,
                            reason=f"Parsed ES/CommonJS import in '{path}' resolving to '{tgt}'",
                            github_url=f"{repo_html_url}/blob/{default_branch}/{path}"
                        )]
                    ))

    # 2. Config Edges: Config/Manifest -> referenced entry or source
    for path in config_paths:
        if path in file_contents:
            content = file_contents[path]
            # If package.json references main / bin
            for ep in entry_point_paths:
                if ep in content and ep != path:
                    add_node(path, path, "config", "confirmed", f"Configuration file {path}")
                    add_node(ep, ep, get_role(ep), "confirmed", f"Referenced entry point {ep}")
                    edge_key = (path, ep, "config")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges_list.append(GraphEdge(
                            source=path,
                            target=ep,
                            type="config",
                            confidence="confirmed",
                            evidence=[Evidence(
                                path=path,
                                reason=f"Configuration in '{path}' directly references '{ep}'",
                                github_url=f"{repo_html_url}/blob/{default_branch}/{path}"
                            )]
                        ))

    # 3. Dependency Edges: Manifest -> Dependency Group
    if dependencies_report:
        for eco in dependencies_report.ecosystems:
            manifest_path = eco.manifest_path
            add_node(manifest_path, manifest_path, "config", "confirmed", f"Manifest file '{manifest_path}'")

            # Runtime group
            if eco.runtime:
                group_id = f"deps:{eco.ecosystem}:runtime"
                add_node(
                    group_id,
                    f"{eco.ecosystem} runtime ({len(eco.runtime)} packages)",
                    "dependency_group",
                    "confirmed",
                    f"Declared in manifest {manifest_path}"
                )
                edge_key = (manifest_path, group_id, "dependency")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append(GraphEdge(
                        source=manifest_path,
                        target=group_id,
                        type="dependency",
                        confidence="confirmed",
                        evidence=[Evidence(
                            path=manifest_path,
                            reason=f"Dependencies declared in manifest '{manifest_path}' (declared, not proven used)",
                            github_url=f"{repo_html_url}/blob/{default_branch}/{manifest_path}"
                        )]
                    ))

            # Dev group
            if eco.dev:
                group_id = f"deps:{eco.ecosystem}:dev"
                add_node(
                    group_id,
                    f"{eco.ecosystem} dev ({len(eco.dev)} packages)",
                    "dependency_group",
                    "confirmed",
                    f"Declared in manifest {manifest_path}"
                )
                edge_key = (manifest_path, group_id, "dependency")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges_list.append(GraphEdge(
                        source=manifest_path,
                        target=group_id,
                        type="dependency",
                        confidence="confirmed",
                        evidence=[Evidence(
                            path=manifest_path,
                            reason=f"Dev dependencies declared in manifest '{manifest_path}' (declared, not proven used)",
                            github_url=f"{repo_html_url}/blob/{default_branch}/{manifest_path}"
                        )]
                    ))

    # Ensure all entry points exist as nodes even if isolated
    for ep in entry_point_paths:
        if ep in all_tree_files:
            add_node(ep, ep, "entry", "confirmed", f"Entry candidate {ep}")

    # 4. Handle Node Capping
    is_capped = len(nodes_map) > max_nodes
    if is_capped:
        warnings.append(AnalysisWarning(
            code="GRAPH_NODE_CAP_REACHED",
            message=f"Architecture graph exceeded {max_nodes} nodes limit ({len(nodes_map)} nodes found). Displaying capped subset."
        ))
        # Prioritize entries, configs, and highly connected nodes
        node_degrees: Dict[str, int] = {nid: 0 for nid in nodes_map}
        for edge in edges_list:
            if edge.source in node_degrees:
                node_degrees[edge.source] += 1
            if edge.target in node_degrees:
                node_degrees[edge.target] += 1

        def sort_key(nid: str):
            node = nodes_map[nid]
            priority = 0
            if node.role == "entry":
                priority += 100
            elif node.role == "config":
                priority += 50
            return (priority, node_degrees.get(nid, 0))

        sorted_node_ids = sorted(nodes_map.keys(), key=sort_key, reverse=True)[:max_nodes]
        capped_node_ids = set(sorted_node_ids)

        nodes = [nodes_map[nid] for nid in sorted_node_ids]
        edges = [e for e in edges_list if e.source in capped_node_ids and e.target in capped_node_ids]
    else:
        nodes = list(nodes_map.values())
        edges = edges_list

    return GraphReport(nodes=nodes, edges=edges, capped=is_capped), warnings
