import pytest
from app.analysis.graph import (
    extract_python_imports,
    extract_js_ts_imports,
    build_architecture_graph,
)
from app.schemas.contract import DependenciesReport, EcosystemDependencies, DependencyItem, Evidence

class TestArchitectureGraph:
    """Test suite for AST/regex import extraction and architecture graph construction."""

    # 1. Python Import Extraction
    def test_python_import_normal(self):
        source = (
            "import os\n"
            "from app.core import app\n"
            "from .utils import helper\n"
        )
        tree_files = {"app/core.py", "app/api/utils.py"}
        targets, warn = extract_python_imports("app/api/routes.py", source, tree_files)
        assert warn is None
        assert "app/core.py" in targets
        assert "app/api/utils.py" in targets
        # Standard library 'os' is not in repo tree files so it should not be included
        assert "os.py" not in targets

    def test_python_import_syntax_error(self):
        source = "def broken( pass"
        targets, warn = extract_python_imports("broken.py", source, set())
        assert targets == []
        assert warn is not None
        assert warn.code == "PYTHON_AST_SYNTAX_ERROR"

    def test_python_unresolved_import(self):
        source = "from nonexistent.module import ghost"
        targets, warn = extract_python_imports("main.py", source, {"main.py"})
        assert targets == []
        assert warn is None

    # 2. JS/TS Import Extraction
    def test_js_ts_import_normal(self):
        source = (
            "import React from 'react';\n"
            "import { Button } from './components/Button';\n"
            "const helper = require('../lib/helper');\n"
            "export * from './types';\n"
        )
        tree_files = {
            "src/components/Button.tsx",
            "lib/helper.js",
            "src/types.ts",
            "src/App.tsx"
        }
        targets = extract_js_ts_imports("src/App.tsx", source, tree_files)
        assert "src/components/Button.tsx" in targets
        assert "lib/helper.js" in targets
        assert "src/types.ts" in targets
        # External package 'react' is not resolved to local tree
        assert "react" not in targets

    # 3. Graph Construction and Circular Import Handling
    def test_graph_circular_imports(self):
        # A imports B, B imports A
        file_contents = {
            "module_a.py": "from .module_b import b\n",
            "module_b.py": "from .module_a import a\n",
        }
        all_tree_files = {"module_a.py", "module_b.py"}
        graph_report, warnings = build_architecture_graph(
            file_contents=file_contents,
            all_tree_files=all_tree_files,
            entry_point_paths=set(),
            config_paths=set()
        )
        assert len(graph_report.nodes) == 2
        assert len(graph_report.edges) == 2
        edge_pairs = {(e.source, e.target) for e in graph_report.edges}
        assert ("module_a.py", "module_b.py") in edge_pairs
        assert ("module_b.py", "module_a.py") in edge_pairs

    # 4. Dependency Group Edges
    def test_graph_dependency_edges(self):
        deps_report = DependenciesReport(
            ecosystems=[
                EcosystemDependencies(
                    ecosystem="npm",
                    manifest_path="package.json",
                    runtime=[DependencyItem(
                        name="react",
                        version_spec="^18.0.0",
                        evidence=Evidence(path="package.json", reason="runtime", github_url="")
                    )],
                    dev=[DependencyItem(
                        name="vite",
                        version_spec="^5.0.0",
                        evidence=Evidence(path="package.json", reason="dev", github_url="")
                    )]
                )
            ]
        )
        graph_report, _ = build_architecture_graph(
            file_contents={},
            all_tree_files={"package.json"},
            entry_point_paths=set(),
            config_paths={"package.json"},
            dependencies_report=deps_report
        )
        # Verify dependency edge types
        dep_edges = [e for e in graph_report.edges if e.type == "dependency"]
        assert len(dep_edges) == 2
        for edge in dep_edges:
            assert edge.source == "package.json"
            assert "deps:npm:" in edge.target
            # Must state declared, not proven used
            assert "declared, not proven used" in edge.evidence[0].reason

    # 5. Node Capping
    def test_graph_node_capping(self):
        # Create 10 files where file_0 imports file_1, file_1 imports file_2, etc.
        all_tree = {f"file_{i}.py" for i in range(20)}
        contents = {
            f"file_{i}.py": f"import file_{i+1}\n" for i in range(19)
        }
        # Cap at 5 nodes
        graph_report, warnings = build_architecture_graph(
            file_contents=contents,
            all_tree_files=all_tree,
            entry_point_paths={"file_0.py"},
            config_paths=set(),
            max_nodes=5
        )
        assert graph_report.capped is True
        assert len(graph_report.nodes) <= 5
        assert any(w.code == "GRAPH_NODE_CAP_REACHED" for w in warnings)
