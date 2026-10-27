import pytest
from app.schemas.contract import RepoMeta
from app.analysis import (
    analyze_languages,
    CatalogIdGenerator,
    detect_ecosystems,
    detect_package_managers,
    detect_frameworks_and_tools,
    detect_config_files,
    detect_entry_points,
    parse_requirements_txt,
    parse_package_json,
    parse_pyproject_toml,
    build_dependencies_report,
    classify_file_kind,
    build_file_tree,
    generate_plain_english_guide,
    ECOSYSTEM_RULES,
    PACKAGE_MANAGER_RULES,
    FRAMEWORK_DEPENDENCY_RULES,
    CONFIG_FILE_RULES,
    HEURISTIC_ENTRY_FILES,
)
from tests.fixtures import (
    FASTAPI_APP_FIXTURE,
    VITE_REACT_APP_FIXTURE,
    NEXTJS_APP_FIXTURE,
    PLAIN_PYTHON_SCRIPT_FIXTURE,
    EMPTY_REPO_FIXTURE,
    NO_README_REPO_FIXTURE,
    MALFORMED_PACKAGE_JSON_FIXTURE,
)

class TestAnalysisEngine:
    """Comprehensive test suite for the deterministic analysis engine."""

    # 1. Languages
    def test_languages_confirmed_from_api(self):
        api_data = {"Python": 8000, "TypeScript": 2000}
        langs = analyze_languages(api_languages=api_data)
        assert len(langs) == 2
        assert langs[0].name == "Python"
        assert langs[0].bytes == 8000
        assert langs[0].percent == 80.0
        assert langs[1].name == "TypeScript"
        assert langs[1].percent == 20.0

    def test_languages_fallback_heuristic_from_tree(self):
        tree = [
            {"path": "app.py", "type": "blob", "size": 300},
            {"path": "lib.py", "type": "blob", "size": 700},
            {"path": "index.html", "type": "blob", "size": 1000},
        ]
        langs = analyze_languages(api_languages={}, tree_nodes=tree)
        assert len(langs) == 2
        assert langs[0].name in ("Python", "HTML")
        total_bytes = sum(l.bytes for l in langs)
        assert total_bytes == 2000

    def test_languages_empty(self):
        langs = analyze_languages(api_languages={}, tree_nodes=[])
        assert langs == []

    # 2. Ecosystem Detection (Covering all ECOSYSTEM_RULES)
    @pytest.mark.parametrize("rule", ECOSYSTEM_RULES)
    def test_all_ecosystem_rules_covered(self, rule):
        id_gen = CatalogIdGenerator()
        marker = rule["marker_files"][0]
        findings = detect_ecosystems({marker}, id_gen)
        assert len(findings) == 1
        assert findings[0].label == rule["name"]
        assert findings[0].confidence == "confirmed"
        assert findings[0].category == "Ecosystem"
        assert findings[0].evidence[0].path == marker

    def test_detect_ecosystems_negative(self):
        id_gen = CatalogIdGenerator()
        paths = {"README.md", "LICENSE", "notes.txt"}
        findings = detect_ecosystems(paths, id_gen)
        assert len(findings) == 0

    # 3. Package Manager Detection (Covering all PACKAGE_MANAGER_RULES)
    @pytest.mark.parametrize("rule", PACKAGE_MANAGER_RULES)
    def test_all_package_manager_rules_covered(self, rule):
        id_gen = CatalogIdGenerator()
        lockfile = rule.get("lockfile") or rule["lockfiles"][0]
        findings = detect_package_managers({lockfile}, id_gen)
        assert len(findings) == 1
        assert findings[0].label == rule["name"]
        assert findings[0].confidence == "confirmed"
        assert findings[0].category == "Package Manager"
        assert findings[0].evidence[0].path == lockfile

    def test_detect_package_managers_negative(self):
        id_gen = CatalogIdGenerator()
        findings = detect_package_managers({"package.json"}, id_gen)
        assert len(findings) == 0

    # 4. Framework and Tooling Detection (Covering all FRAMEWORK_DEPENDENCY_RULES)
    @pytest.mark.parametrize("rule", FRAMEWORK_DEPENDENCY_RULES)
    def test_all_framework_dependency_rules_covered(self, rule):
        id_gen = CatalogIdGenerator()
        dep = rule["dep"]
        findings = detect_frameworks_and_tools({dep}, {dep: "manifest.json"}, id_gen)
        assert len(findings) == 1
        assert findings[0].label == rule["name"]
        assert findings[0].confidence == "confirmed"
        assert findings[0].category == rule["category"]
        assert "Declared in manifest" in findings[0].evidence[0].reason

    def test_detect_frameworks_negative(self):
        id_gen = CatalogIdGenerator()
        deps = {"left-pad", "chalk", "requests"}
        findings = detect_frameworks_and_tools(deps, {}, id_gen)
        assert len(findings) == 0

    # 5. Config File Detection (Covering all CONFIG_FILE_RULES)
    @pytest.mark.parametrize("rule", CONFIG_FILE_RULES)
    def test_all_config_file_rules_covered(self, rule):
        id_gen = CatalogIdGenerator()
        file_path = rule.get("filename") or (rule["pattern"] + "js" if rule["pattern"].endswith(".") else rule["pattern"] + "test.yml")
        findings = detect_config_files({file_path}, id_gen)
        assert len(findings) == 1
        assert findings[0].label == rule["name"]
        assert findings[0].confidence == "confirmed"
        assert findings[0].category == "Configuration"

    # 6. Entry Points Detection
    def test_detect_entry_points_package_json(self):
        id_gen = CatalogIdGenerator()
        pkg_json = '{"main": "dist/index.js", "bin": {"mycli": "bin/run.js"}, "scripts": {"start": "node dist/index.js"}}'
        manifests = {"package.json": pkg_json}
        findings = detect_entry_points(set(), manifests, {}, id_gen)
        labels = [f.label for f in findings]
        assert "Package Entry Candidate (main)" in labels
        assert "CLI Binary Entry Candidate (mycli)" in labels
        assert "Script Runner Candidate (npm run start)" in labels
        for f in findings:
            assert "Candidate" in f.label

    def test_detect_entry_points_dockerfile(self):
        id_gen = CatalogIdGenerator()
        files = {"Dockerfile": "FROM python:3.11\nCMD [\"python\", \"app.py\"]\n"}
        findings = detect_entry_points(set(), {}, files, id_gen)
        assert len(findings) == 1
        assert "Container CMD Entry Candidate" in findings[0].label

    def test_detect_entry_points_python_main_guard(self):
        id_gen = CatalogIdGenerator()
        files = {"server.py": "def start(): pass\nif __name__ == '__main__': start()\n"}
        findings = detect_entry_points({"server.py"}, {}, files, id_gen)
        labels = [f.label for f in findings]
        assert "Python Executable Guard Candidate" in labels

    @pytest.mark.parametrize("rule", HEURISTIC_ENTRY_FILES)
    def test_heuristic_entry_files_covered(self, rule):
        id_gen = CatalogIdGenerator()
        findings = detect_entry_points({rule["path"]}, {}, {}, id_gen)
        assert len(findings) == 1
        assert findings[0].confidence == "heuristic"
        assert "Application Entry Candidate" in findings[0].label

    def test_detect_entry_points_nextjs_routers(self):
        id_gen = CatalogIdGenerator()
        findings_pages = detect_entry_points({"pages/index.tsx"}, {}, {}, id_gen)
        assert any("Next.js Pages Router" in f.label for f in findings_pages)

        findings_app = detect_entry_points({"app/page.tsx"}, {}, {}, id_gen)
        assert any("Next.js App Router" in f.label for f in findings_app)

    # 7. Manifest Parsers
    def test_parse_requirements_txt_complex(self):
        content = (
            "# Top level comment\n"
            "fastapi==0.100.0\n"
            "uvicorn[standard]>=0.20.0 # inline comment\n"
            "pydantic~=2.0; python_version >= '3.8'\n"
            "-r base.txt\n"
            "-i https://pypi.org/simple\n"
            "git+https://github.com/encode/httpx.git@main#egg=httpx\n"
            "invalid line without format\n"
        )
        items, warnings = parse_requirements_txt(content)
        names = [i.name for i in items]
        assert "fastapi" in names
        assert "uvicorn" in names
        assert "pydantic" in names
        assert "httpx" in names

        warning_codes = [w.code for w in warnings]
        assert "REQUIREMENTS_RECURSIVE_INCLUDE" in warning_codes
        assert "REQUIREMENTS_UNPARSED_LINE" in warning_codes

    def test_parse_package_json_malformed(self):
        runtime, dev, warnings = parse_package_json("{ broken json ")
        assert len(runtime) == 0
        assert len(dev) == 0
        assert len(warnings) == 1
        assert warnings[0].code == "MALFORMED_PACKAGE_JSON"

    def test_parse_pyproject_toml_pep621_and_poetry(self):
        content = (
            "[project]\n"
            'name = "my-project"\n'
            'dependencies = ["fastapi>=0.95.0", "requests[security]>=2.28"]\n'
            "[project.optional-dependencies]\n"
            'dev = ["pytest>=7.0", "black"]\n'
            "[tool.poetry.dependencies]\n"
            'python = "^3.11"\n'
            'httpx = "^0.24"\n'
        )
        runtime, dev, warnings = parse_pyproject_toml(content)
        runtime_names = [i.name for i in runtime]
        dev_names = [i.name for i in dev]
        assert "fastapi" in runtime_names
        assert "requests" in runtime_names
        assert "httpx" in runtime_names
        assert "python" not in runtime_names
        assert "pytest" in dev_names

    # 8. File Tree Builder
    def test_file_tree_classification(self):
        tree_raw = [
            {"path": "src/main.ts", "type": "blob", "size": 100},
            {"path": "tests/test_api.py", "type": "blob", "size": 200},
            {"path": "package.json", "type": "blob", "size": 300},
            {"path": "README.md", "type": "blob", "size": 400},
            {"path": "dist/bundle.js", "type": "blob", "size": 500},
            {"path": ".github/workflows/test.yml", "type": "blob", "size": 600},
            {"path": "data.json", "type": "blob", "size": 700},
            {"path": "logo.svg", "type": "blob", "size": 800},
            {"path": "yarn.lock", "type": "blob", "size": 900},
            {"path": "unknown.xyz", "type": "blob", "size": 50},
        ]
        report = build_file_tree(tree_raw)
        kinds = {n.path: n.file_kind for n in report.nodes}
        assert kinds["src/main.ts"] == "source"
        assert kinds["tests/test_api.py"] == "test"
        assert kinds["package.json"] == "config"
        assert kinds["README.md"] == "docs"
        assert kinds["dist/bundle.js"] == "build"
        assert kinds[".github/workflows/test.yml"] == "ci"
        assert kinds["data.json"] == "data"
        assert kinds["logo.svg"] == "asset"
        assert kinds["yarn.lock"] == "lockfile"
        assert kinds["unknown.xyz"] == "unknown"

        desc_map = {n.path: n.description for n in report.nodes}
        assert desc_map["package.json"] is not None
        assert desc_map["README.md"] is not None
        assert desc_map["yarn.lock"] is not None
        assert desc_map["unknown.xyz"] is None

    # 9. Plain-English Guide Generation
    def test_generate_plain_english_guide(self):
        repo_meta = RepoMeta(
            owner="testorg",
            name="app",
            full_name="testorg/app",
            description="Sample app",
            html_url="https://github.com/testorg/app",
            default_branch="main",
            stars=10,
            forks=2,
            open_issues=0,
            license="MIT",
            primary_language="Python",
            topics=[],
            size_kb=100,
            pushed_at="2026-01-01T00:00:00Z",
            archived=False
        )
        langs = analyze_languages(api_languages={"Python": 1000})
        id_gen = CatalogIdGenerator()
        tech = detect_ecosystems({"requirements.txt"}, id_gen)
        fw = detect_frameworks_and_tools({"fastapi"}, {"fastapi": "requirements.txt"}, id_gen)
        tech.extend(fw)
        configs = detect_config_files({"pytest.ini"}, id_gen)
        eps = detect_entry_points({"main.py"}, {}, {}, id_gen)

        guide = generate_plain_english_guide(
            repo_meta=repo_meta,
            languages=langs,
            tech_stack=tech,
            config_files=configs,
            entry_points=eps,
            dependencies_ecosystems=["pip"]
        )

        assert len(guide) >= 3
        for section in guide:
            assert len(section.title) > 0
            assert len(section.body) > 0
            assert len(section.finding_refs) > 0
            assert all(ref.startswith("ART-") for ref in section.finding_refs)

    # 10. End-to-End Fixture Runs
    def test_fastapi_fixture_analysis(self):
        f = FASTAPI_APP_FIXTURE
        id_gen = CatalogIdGenerator()
        file_paths = {n["path"] for n in f["tree"]}

        ecosystems = detect_ecosystems(file_paths, id_gen)
        assert any(e.label == "Python" for e in ecosystems)

        deps_report, warnings = build_dependencies_report(f["manifests"])
        dep_names = {i.name for eco in deps_report.ecosystems for i in eco.runtime}
        assert "fastapi" in dep_names

        fw_findings = detect_frameworks_and_tools(
            dep_names, {i.name: eco.manifest_path for eco in deps_report.ecosystems for i in eco.runtime}, id_gen
        )
        assert any(finding.label == "FastAPI" for finding in fw_findings)

        eps = detect_entry_points(file_paths, f["manifests"], f["files"], id_gen)
        ep_labels = [ep.label for ep in eps]
        assert any("Container CMD" in l for l in ep_labels)
        assert any("Python Executable Guard" in l for l in ep_labels)

    def test_vite_react_fixture_analysis(self):
        f = VITE_REACT_APP_FIXTURE
        id_gen = CatalogIdGenerator()
        file_paths = {n["path"] for n in f["tree"]}

        ecosystems = detect_ecosystems(file_paths, id_gen)
        assert any(e.label == "Node.js / npm" for e in ecosystems)

        pms = detect_package_managers(file_paths, id_gen)
        assert any(pm.label == "npm" for pm in pms)

        deps_report, _ = build_dependencies_report(f["manifests"])
        all_deps = {i.name for eco in deps_report.ecosystems for i in eco.runtime + eco.dev}
        assert "react" in all_deps
        assert "vite" in all_deps

        fw = detect_frameworks_and_tools(all_deps, {k: "package.json" for k in all_deps}, id_gen)
        fw_labels = [finding.label for finding in fw]
        assert "React" in fw_labels
        assert "Vite" in fw_labels
        assert "Tailwind CSS" in fw_labels

    def test_nextjs_fixture_analysis(self):
        f = NEXTJS_APP_FIXTURE
        id_gen = CatalogIdGenerator()
        file_paths = {n["path"] for n in f["tree"]}
        deps_report, _ = build_dependencies_report(f["manifests"])
        dep_names = {i.name for eco in deps_report.ecosystems for i in eco.runtime}
        assert "next" in dep_names
        fw = detect_frameworks_and_tools(dep_names, {k: "package.json" for k in dep_names}, id_gen)
        assert any(finding.label == "Next.js" for finding in fw)

    def test_plain_python_script_fixture_analysis(self):
        f = PLAIN_PYTHON_SCRIPT_FIXTURE
        id_gen = CatalogIdGenerator()
        file_paths = {n["path"] for n in f["tree"]}
        eps = detect_entry_points(file_paths, f["manifests"], f["files"], id_gen)
        assert any("Python Executable Guard" in ep.label for ep in eps)

    def test_no_readme_repo_fixture_analysis(self):
        f = NO_README_REPO_FIXTURE
        tree = build_file_tree(f["tree"])
        readme_nodes = [n for n in tree.nodes if n.path == "README.md"]
        assert len(readme_nodes) == 0

    def test_empty_repo_fixture_analysis(self):
        f = EMPTY_REPO_FIXTURE
        id_gen = CatalogIdGenerator()
        ecosystems = detect_ecosystems(set(), id_gen)
        assert len(ecosystems) == 0
        deps_report, warnings = build_dependencies_report(f["manifests"])
        assert len(deps_report.ecosystems) == 0
        tree = build_file_tree(f["tree"])
        assert len(tree.nodes) == 0

    def test_malformed_package_json_fixture_analysis(self):
        f = MALFORMED_PACKAGE_JSON_FIXTURE
        deps_report, warnings = build_dependencies_report(f["manifests"])
        assert len(warnings) > 0
        assert warnings[0].code == "MALFORMED_PACKAGE_JSON"
