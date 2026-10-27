"""
Detection rules table for Repo Archaeologist.
All rules are stored as deterministic data structures.
"""
from typing import Dict, List, Any, Optional

# Well-known file descriptions (only for well-known files, otherwise description is None)
WELL_KNOWN_FILE_DESCRIPTIONS: Dict[str, str] = {
    "package.json": "Node.js package manifest and dependency definitions",
    "package-lock.json": "npm dependency lockfile with pinned versions",
    "yarn.lock": "Yarn dependency lockfile with pinned versions",
    "pnpm-lock.yaml": "pnpm dependency lockfile with pinned versions",
    "bun.lockb": "Bun binary dependency lockfile",
    "bun.lock": "Bun text dependency lockfile",
    "requirements.txt": "Python dependencies declaration file",
    "pyproject.toml": "Python project configuration and build system specification",
    "setup.py": "Python package setup and distribution script",
    "setup.cfg": "Python package configuration file",
    "Pipfile": "Pipenv dependency specification",
    "Pipfile.lock": "Pipenv pinned dependency lockfile",
    "poetry.lock": "Poetry pinned dependency lockfile",
    "uv.lock": "uv pinned dependency lockfile",
    "Dockerfile": "Docker container build instructions",
    "docker-compose.yml": "Multi-container Docker application service definition",
    "docker-compose.yaml": "Multi-container Docker application service definition",
    "tsconfig.json": "TypeScript compiler configuration options",
    "vite.config.ts": "Vite frontend build tool and dev server configuration",
    "vite.config.js": "Vite frontend build tool and dev server configuration",
    "next.config.js": "Next.js application configuration",
    "next.config.mjs": "Next.js application configuration",
    "next.config.ts": "Next.js application configuration",
    "tailwind.config.js": "Tailwind CSS utility configuration",
    "tailwind.config.ts": "Tailwind CSS utility configuration",
    "tailwind.config.cjs": "Tailwind CSS utility configuration",
    "postcss.config.js": "PostCSS CSS processor configuration",
    "postcss.config.cjs": "PostCSS CSS processor configuration",
    "eslint.config.js": "ESLint flat configuration",
    ".eslintrc.json": "ESLint linter configuration",
    ".eslintrc.js": "ESLint linter configuration",
    ".gitignore": "Git version control path exclusion list",
    "README.md": "Repository documentation and project overview",
    "LICENSE": "Software licensing terms and permissions",
    "pytest.ini": "Pytest test framework configuration",
    "Makefile": "Make build automation instructions",
    "Procfile": "Process types declaration for container/PaaS runners",
}

# Ecosystem Rules: mapped from marker files
ECOSYSTEM_RULES = [
    {
        "id": "ECO-NPM",
        "marker_files": ["package.json"],
        "name": "Node.js / npm",
        "category": "Ecosystem",
        "confidence": "confirmed",
        "reason": "Presence of 'package.json' manifest in repository",
    },
    {
        "id": "ECO-PYTHON",
        "marker_files": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
        "name": "Python",
        "category": "Ecosystem",
        "confidence": "confirmed",
        "reason": "Presence of Python project manifest ({marker}) in repository",
    },
    {
        "id": "ECO-GO",
        "marker_files": ["go.mod"],
        "name": "Go",
        "category": "Ecosystem",
        "confidence": "confirmed",
        "reason": "Presence of 'go.mod' module definition in repository",
    },
    {
        "id": "ECO-RUST",
        "marker_files": ["Cargo.toml"],
        "name": "Rust / Cargo",
        "category": "Ecosystem",
        "confidence": "confirmed",
        "reason": "Presence of 'Cargo.toml' crate manifest in repository",
    },
]

# Package Manager Rules: mapped from lockfiles / manifest configs
PACKAGE_MANAGER_RULES = [
    {
        "id": "PM-NPM",
        "lockfile": "package-lock.json",
        "name": "npm",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'package-lock.json' lockfile",
    },
    {
        "id": "PM-YARN",
        "lockfile": "yarn.lock",
        "name": "Yarn",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'yarn.lock' lockfile",
    },
    {
        "id": "PM-PNPM",
        "lockfile": "pnpm-lock.yaml",
        "name": "pnpm",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'pnpm-lock.yaml' lockfile",
    },
    {
        "id": "PM-BUN",
        "lockfiles": ["bun.lockb", "bun.lock"],
        "name": "Bun",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of Bun lockfile ({lockfile})",
    },
    {
        "id": "PM-POETRY",
        "lockfile": "poetry.lock",
        "name": "Poetry",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'poetry.lock' lockfile",
    },
    {
        "id": "PM-UV",
        "lockfile": "uv.lock",
        "name": "uv",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'uv.lock' lockfile",
    },
    {
        "id": "PM-PIPENV",
        "lockfile": "Pipfile.lock",
        "name": "Pipenv",
        "category": "Package Manager",
        "confidence": "confirmed",
        "reason": "Presence of 'Pipfile.lock' lockfile",
    },
]

# Framework and Tooling Rules: declared in dependencies (confirmed) or matched by config file (confirmed)
FRAMEWORK_DEPENDENCY_RULES = [
    # JS / TS Frameworks & Libraries
    {"dep": "react", "name": "React", "category": "Framework", "summary": "Frontend component library for building user interfaces"},
    {"dep": "next", "name": "Next.js", "category": "Framework", "summary": "React server-rendered and static web framework"},
    {"dep": "vue", "name": "Vue.js", "category": "Framework", "summary": "Progressive JavaScript framework for user interfaces"},
    {"dep": "nuxt", "name": "Nuxt", "category": "Framework", "summary": "Intuitive Vue framework for web applications"},
    {"dep": "svelte", "name": "Svelte", "category": "Framework", "summary": "Compile-step component framework for web applications"},
    {"dep": "@angular/core", "name": "Angular", "category": "Framework", "summary": "TypeScript-based component web framework"},
    {"dep": "vite", "name": "Vite", "category": "Tooling", "summary": "Next-generation frontend development server and bundler"},
    {"dep": "express", "name": "Express", "category": "Framework", "summary": "Fast, unopinionated web framework for Node.js"},
    {"dep": "nestjs", "name": "NestJS", "category": "Framework", "summary": "Progressive Node.js framework for scalable server applications"},
    {"dep": "@nestjs/core", "name": "NestJS", "category": "Framework", "summary": "Progressive Node.js framework for scalable server applications"},
    {"dep": "tailwindcss", "name": "Tailwind CSS", "category": "Styling", "summary": "Utility-first CSS framework for rapid UI development"},
    {"dep": "typescript", "name": "TypeScript", "category": "Tooling", "summary": "Typed superset of JavaScript that compiles to plain JavaScript"},
    {"dep": "vitest", "name": "Vitest", "category": "Testing", "summary": "Vite-native unit test framework"},
    {"dep": "jest", "name": "Jest", "category": "Testing", "summary": "Delightful JavaScript testing framework"},
    # Python Frameworks & Libraries
    {"dep": "fastapi", "name": "FastAPI", "category": "Framework", "summary": "Modern, fast web framework for building APIs with Python"},
    {"dep": "flask", "name": "Flask", "category": "Framework", "summary": "Lightweight WSGI web application framework"},
    {"dep": "django", "name": "Django", "category": "Framework", "summary": "High-level Python web framework encouraging rapid development"},
    {"dep": "pytest", "name": "Pytest", "category": "Testing", "summary": "Python testing framework for simple and scalable test suites"},
    {"dep": "numpy", "name": "NumPy", "category": "Data Science", "summary": "Fundamental package for scientific computing with Python"},
    {"dep": "pandas", "name": "Pandas", "category": "Data Science", "summary": "Data analysis and manipulation library for Python"},
    {"dep": "torch", "name": "PyTorch", "category": "Machine Learning", "summary": "Deep learning and tensor computation library"},
    {"dep": "tensorflow", "name": "TensorFlow", "category": "Machine Learning", "summary": "End-to-end open source platform for machine learning"},
    {"dep": "scikit-learn", "name": "scikit-learn", "category": "Machine Learning", "summary": "Machine learning and data mining library in Python"},
]

# Config File Rules
CONFIG_FILE_RULES = [
    {"pattern": "vite.config.", "name": "Vite Configuration", "summary": "Build configuration for Vite dev server and bundler"},
    {"pattern": "next.config.", "name": "Next.js Configuration", "summary": "Runtime and build settings for Next.js application"},
    {"pattern": "tailwind.config.", "name": "Tailwind Configuration", "summary": "Utility style theme configuration and content paths"},
    {"filename": "tsconfig.json", "name": "TypeScript Configuration", "summary": "Compiler options and project type boundaries"},
    {"filename": "Dockerfile", "name": "Docker Container", "summary": "Automated container build specification"},
    {"pattern": "docker-compose.", "name": "Docker Compose", "summary": "Multi-container application service orchestrator"},
    {"pattern": ".github/workflows/", "name": "GitHub Actions CI/CD", "summary": "Automated CI/CD build, test, and deployment workflows"},
    {"pattern": ".eslintrc", "name": "ESLint Configuration", "summary": "JavaScript and TypeScript static analysis rules"},
    {"filename": "eslint.config.js", "name": "ESLint Configuration", "summary": "JavaScript and TypeScript flat linter configuration"},
    {"filename": "pytest.ini", "name": "Pytest Configuration", "summary": "Python test runner configuration settings"},
    {"filename": "Makefile", "name": "Makefile", "summary": "Target build automation directives"},
]

# Entry Point Heuristic Patterns
HEURISTIC_ENTRY_FILES = [
    {"path": "main.py", "reason": "Standard root Python executable entry file"},
    {"path": "app.py", "reason": "Standard application initialization file"},
    {"path": "manage.py", "reason": "Standard Django administrative entry point"},
    {"path": "wsgi.py", "reason": "WSGI server entry point"},
    {"path": "asgi.py", "reason": "ASGI asynchronous server entry point"},
    {"path": "__main__.py", "reason": "Python module direct execution entry file"},
    {"path": "index.js", "reason": "Root JavaScript entry point"},
    {"path": "index.ts", "reason": "Root TypeScript entry point"},
    {"path": "server.js", "reason": "Server process entry point"},
    {"path": "server.ts", "reason": "Server process entry point"},
    {"path": "src/main.py", "reason": "Source directory Python entry file"},
    {"path": "src/app.py", "reason": "Source directory application initialization file"},
    {"path": "src/index.js", "reason": "Source directory root script"},
    {"path": "src/index.ts", "reason": "Source directory TypeScript entry point"},
    {"path": "src/main.ts", "reason": "Vite/browser application bootstrap file"},
    {"path": "src/main.tsx", "reason": "React application mount entry point"},
    {"path": "src/App.tsx", "reason": "React root component candidate"},
    {"path": "src/App.jsx", "reason": "React root component candidate"},
]
