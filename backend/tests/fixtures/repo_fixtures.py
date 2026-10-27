"""
Realistic test repository fixtures for Repo Archaeologist analysis engine.
All fixtures represent realistic trees, manifests, and file contents.
"""

FASTAPI_APP_FIXTURE = {
    "repo": {
        "owner": "testorg",
        "name": "fastapi-sample",
        "full_name": "testorg/fastapi-sample",
        "description": "Sample production FastAPI service",
        "html_url": "https://github.com/testorg/fastapi-sample",
        "default_branch": "main",
        "stars": 120,
        "forks": 15,
        "open_issues": 2,
        "license": "MIT",
        "primary_language": "Python",
        "topics": ["fastapi", "python", "api"],
        "size_kb": 250,
        "pushed_at": "2026-03-01T12:00:00Z",
        "archived": False,
    },
    "languages": {"Python": 150000, "Dockerfile": 2000},
    "tree": [
        {"path": "requirements.txt", "type": "blob", "size": 150},
        {"path": "main.py", "type": "blob", "size": 850},
        {"path": "Dockerfile", "type": "blob", "size": 420},
        {"path": "pytest.ini", "type": "blob", "size": 60},
        {"path": "app", "type": "tree"},
        {"path": "app/__init__.py", "type": "blob", "size": 0},
        {"path": "app/core.py", "type": "blob", "size": 1200},
        {"path": "tests", "type": "tree"},
        {"path": "tests/test_api.py", "type": "blob", "size": 600},
        {"path": "README.md", "type": "blob", "size": 1400},
        {"path": ".gitignore", "type": "blob", "size": 100},
    ],
    "manifests": {
        "requirements.txt": (
            "# Core dependencies\n"
            "fastapi==0.100.0\n"
            "uvicorn[standard]>=0.20.0\n"
            "pydantic>=2.0\n"
            "# Development tools\n"
            "pytest>=7.0.0\n"
        )
    },
    "files": {
        "main.py": (
            "from app.core import app\n"
            "import uvicorn\n\n"
            "if __name__ == '__main__':\n"
            "    uvicorn.run(app, host='0.0.0.0', port=8000)\n"
        ),
        "Dockerfile": (
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install -r requirements.txt\n"
            "COPY . .\n"
            "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\"]\n"
        ),
        "app/core.py": (
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
        )
    }
}

VITE_REACT_APP_FIXTURE = {
    "repo": {
        "owner": "webdev",
        "name": "vite-react-ts",
        "full_name": "webdev/vite-react-ts",
        "description": "Modern React frontend built with Vite",
        "html_url": "https://github.com/webdev/vite-react-ts",
        "default_branch": "main",
        "stars": 450,
        "forks": 30,
        "open_issues": 1,
        "license": "Apache-2.0",
        "primary_language": "TypeScript",
        "topics": ["react", "vite", "typescript"],
        "size_kb": 410,
        "pushed_at": "2026-02-15T10:00:00Z",
        "archived": False,
    },
    "languages": {"TypeScript": 85000, "HTML": 3000, "CSS": 12000},
    "tree": [
        {"path": "package.json", "type": "blob", "size": 890},
        {"path": "package-lock.json", "type": "blob", "size": 45000},
        {"path": "tsconfig.json", "type": "blob", "size": 600},
        {"path": "vite.config.ts", "type": "blob", "size": 350},
        {"path": "tailwind.config.ts", "type": "blob", "size": 400},
        {"path": "index.html", "type": "blob", "size": 500},
        {"path": "src", "type": "tree"},
        {"path": "src/main.tsx", "type": "blob", "size": 650},
        {"path": "src/App.tsx", "type": "blob", "size": 1200},
        {"path": "src/index.css", "type": "blob", "size": 400},
        {"path": "README.md", "type": "blob", "size": 2000},
    ],
    "manifests": {
        "package.json": (
            "{\n"
            '  "name": "vite-react-ts",\n'
            '  "version": "1.0.0",\n'
            '  "scripts": {\n'
            '    "dev": "vite",\n'
            '    "build": "tsc && vite build"\n'
            "  },\n"
            '  "dependencies": {\n'
            '    "react": "^18.2.0",\n'
            '    "react-dom": "^18.2.0",\n'
            '    "lucide-react": "^0.300.0"\n'
            "  },\n"
            '  "devDependencies": {\n'
            '    "vite": "^5.0.0",\n'
            '    "typescript": "^5.2.0",\n'
            '    "tailwindcss": "^3.4.0",\n'
            '    "vitest": "^1.0.0"\n'
            "  }\n"
            "}\n"
        )
    },
    "files": {
        "vite.config.ts": "import { defineConfig } from 'vite'; export default defineConfig({});",
        "src/main.tsx": "import React from 'react'; import App from './App'; import './index.css';",
        "src/App.tsx": "export default function App() { return <div>App</div>; }"
    }
}

NEXTJS_APP_FIXTURE = {
    "repo": {
        "owner": "company",
        "name": "nextjs-portal",
        "full_name": "company/nextjs-portal",
        "description": "Customer portal in Next.js",
        "html_url": "https://github.com/company/nextjs-portal",
        "default_branch": "main",
        "stars": 80,
        "forks": 5,
        "open_issues": 0,
        "license": None,
        "primary_language": "TypeScript",
        "topics": [],
        "size_kb": 800,
        "pushed_at": "2026-01-20T08:00:00Z",
        "archived": False,
    },
    "languages": {"TypeScript": 90000},
    "tree": [
        {"path": "package.json", "type": "blob", "size": 600},
        {"path": "pnpm-lock.yaml", "type": "blob", "size": 30000},
        {"path": "next.config.js", "type": "blob", "size": 250},
        {"path": "app", "type": "tree"},
        {"path": "app/layout.tsx", "type": "blob", "size": 800},
        {"path": "app/page.tsx", "type": "blob", "size": 1100},
        {"path": "README.md", "type": "blob", "size": 500},
    ],
    "manifests": {
        "package.json": (
            "{\n"
            '  "name": "nextjs-portal",\n'
            '  "dependencies": {\n'
            '    "next": "14.0.0",\n'
            '    "react": "18.2.0"\n'
            "  }\n"
            "}\n"
        )
    },
    "files": {
        "next.config.js": "module.exports = {};"
    }
}

PLAIN_PYTHON_SCRIPT_FIXTURE = {
    "repo": {
        "owner": "coder",
        "name": "utility-script",
        "full_name": "coder/utility-script",
        "description": "Single-file helper script",
        "html_url": "https://github.com/coder/utility-script",
        "default_branch": "master",
        "stars": 10,
        "forks": 1,
        "open_issues": 0,
        "license": "MIT",
        "primary_language": "Python",
        "topics": [],
        "size_kb": 20,
        "pushed_at": "2025-11-01T00:00:00Z",
        "archived": False,
    },
    "languages": {"Python": 2500},
    "tree": [
        {"path": "main.py", "type": "blob", "size": 2500},
        {"path": "README.md", "type": "blob", "size": 400},
    ],
    "manifests": {},
    "files": {
        "main.py": (
            "import os\n"
            "import sys\n\n"
            "def run():\n"
            "    print('Processing...')\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n"
        )
    }
}

EMPTY_REPO_FIXTURE = {
    "repo": {
        "owner": "ghost",
        "name": "empty-site",
        "full_name": "ghost/empty-site",
        "description": "Completely empty repository",
        "html_url": "https://github.com/ghost/empty-site",
        "default_branch": "main",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "license": None,
        "primary_language": None,
        "topics": [],
        "size_kb": 0,
        "pushed_at": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    "languages": {},
    "tree": [],
    "manifests": {},
    "files": {}
}

NO_README_REPO_FIXTURE = {
    "repo": {
        "owner": "dev",
        "name": "no-readme",
        "full_name": "dev/no-readme",
        "description": None,
        "html_url": "https://github.com/dev/no-readme",
        "default_branch": "main",
        "stars": 5,
        "forks": 0,
        "open_issues": 1,
        "license": None,
        "primary_language": "JavaScript",
        "topics": [],
        "size_kb": 50,
        "pushed_at": "2025-06-01T00:00:00Z",
        "archived": False,
    },
    "languages": {"JavaScript": 3500},
    "tree": [
        {"path": "index.js", "type": "blob", "size": 1500},
        {"path": "package.json", "type": "blob", "size": 200},
    ],
    "manifests": {
        "package.json": '{"name": "no-readme", "main": "index.js"}'
    },
    "files": {
        "index.js": "console.log('Hello');"
    }
}

MALFORMED_PACKAGE_JSON_FIXTURE = {
    "repo": {
        "owner": "tester",
        "name": "broken-manifest",
        "full_name": "tester/broken-manifest",
        "description": "Repo with broken package.json",
        "html_url": "https://github.com/tester/broken-manifest",
        "default_branch": "main",
        "stars": 2,
        "forks": 0,
        "open_issues": 0,
        "license": None,
        "primary_language": "JavaScript",
        "topics": [],
        "size_kb": 30,
        "pushed_at": "2025-08-01T00:00:00Z",
        "archived": False,
    },
    "languages": {"JavaScript": 500},
    "tree": [
        {"path": "package.json", "type": "blob", "size": 100},
    ],
    "manifests": {
        "package.json": '{"name": "broken", "dependencies": {INVALID JSON'
    },
    "files": {}
}
