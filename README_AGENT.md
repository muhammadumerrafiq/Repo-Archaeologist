# Repo Archaeologist: Master Build Instructions

> **Token note:** the human places the GitHub token in `backend/.env` personally. Never ask for it, print it, or open that file (see 1.4).
>
> **How to use this file:** Save it in the project root as `README_AGENT.md`. Tell the agent: *"Read README_AGENT.md fully. Start with Phase 0. Complete one phase at a time. Stop at the end of each phase, report, and wait for my approval."*

---

## 0. Mission

Build **Repo Archaeologist**, a real, working developer tool. A user pastes a public GitHub repository URL and receives a visual, beginner-friendly explanation of the repository: its structure, key files, dependencies, and architecture.

This is a **working application**, not a mockup or static dashboard. All analysis comes from real GitHub API data and deterministic rules.

---

## 1. Non-negotiable rules (read before every phase)

### 1.1 Honesty protocol (anti-hallucination)
1. **Never claim a test, build, lint, or command passed unless you ran it in this session and can paste the real output.** If you did not run it, write "NOT RUN".
2. **Never invent package names or versions.** Before pinning any dependency, verify it:
   - npm: `npm view <package> version`
   - pip: `pip index versions <package>`
3. **Never invent GitHub API endpoints or response fields.** Use only fields you have seen in a real API response (call it and inspect) or in the official docs at https://docs.github.com/en/rest.
4. **Never fabricate analysis results, sample outputs, or screenshots.** If the GitHub API is rate limited, say so and stop. Do not simulate data.
5. **Never use mock data in the final application.** Fixtures are allowed only inside tests.
6. If something fails, is skipped, or is uncertain, list it under **"Not done / Problems"** in your report. Reporting problems is success. Hiding them is failure.
7. If a requirement is ambiguous, state your assumption explicitly in the plan instead of silently choosing.
8. Do not add features that are not in this document.

### 1.2 Safety rules
1. **Never execute, install, import, or run code from analyzed repositories.** Analysis is read-only text parsing.
2. **Only public repositories.** Never request write permissions or OAuth scopes.
3. **The GitHub token (optional) lives only in the backend environment variable `GITHUB_TOKEN`.** It must never appear in frontend code, API responses, logs, error messages, or the built frontend bundle.
4. **Never commit real credentials.** Provide `.env.example` with placeholders only. `.env` must be in `.gitignore`.
5. **SSRF protection:** the backend may only contact `api.github.com` and `raw.githubusercontent.com`. User input is never used as a free-form URL for requests.
6. **No `git push`, no deployment, no publishing packages.** Local commits only, and only if I ask.
7. **CORS** allows only `http://localhost:5173` and `http://127.0.0.1:5173` (configurable via env). No wildcard.

### 1.3 Analysis integrity rules
1. Use **deterministic rules** only. Do **not** claim AI-generated explanations. The UI and README must not say "AI-powered".
2. Every finding carries:
   - `label`: human-readable name
   - `confidence`: `"confirmed"` or `"heuristic"`
   - `evidence[]`: each item has `path`, `reason`, and `github_url`
3. **Confirmed** means directly observable fact (for example, `package.json` exists and lists `vite` under `devDependencies`; a parsed `import` statement resolves to a repo file).
4. **Heuristic** means inferred from naming or convention (for example, `src/main.tsx` is *likely* an entry point).
5. Never state that a dependency is "used". Say **"declared in manifest"**.
6. Never claim every detected file is an execution entry point. Call them **"entry point candidates"**.
7. Every sentence in the plain-English guide must trace to a finding. No invented descriptions.

### 1.4 GitHub token setup (classic personal access token)

The project uses an **optional** GitHub classic personal access token to raise the API rate limit (unauthenticated is about 60 requests per hour; authenticated is much higher). The token is **read-only for public data**.

**Owner's setup (done by the human, not the agent):**
1. The token is created with **no scopes ticked** (public data needs none). Do not request `repo`, `workflow`, `write:*` or any other scope.
2. The human creates `backend/.env` by copying `backend/.env.example` and pastes the token there: `GITHUB_TOKEN=<token>`.
3. The token is never pasted into chat, into this file, into source code, or into tests.

**Agent rules for the token:**
1. Read it only from the environment variable `GITHUB_TOKEN`, only in backend code (`config.py`), and send it only as an `Authorization` header to `api.github.com`. Never send it to `raw.githubusercontent.com` unless the plan shows that is required and safe.
2. **Never open, print, echo, `cat`, log, or quote the contents of `backend/.env`.** If you need to know whether a token is configured, use the health endpoint's boolean (below).
3. `.env` must be git-ignored. Prove it with `git check-ignore -v backend/.env` and paste the output.
4. `GET /api/health` returns `{ "status": "ok", "github_token_configured": true|false }`. It must never return the token, a prefix of it, or its length.
5. On startup or on a dedicated check, you may call `GET https://api.github.com/rate_limit` and report **only** the numeric limit and remaining count, so I can see whether the token works. Never print request headers.
6. Redact `Authorization` headers from all logs and from every error message and exception text.
7. Add a test proving the token string never appears in any API response or log output (use a fake token value such as `test-token-123` in the test).
8. Phase 8 must grep the built frontend (`dist/`) and the repository for token-like strings (`ghp_`, `github_pat_`) and report the real result.
9. If the app runs without a token it must still work, with a visible warning about the lower rate limit.

**If the token is ever exposed** (committed, pasted in chat, shown in output), tell me immediately and I will revoke it in GitHub Settings, then create a new one.

---

## 2. Tech stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide React, React Flow (use the current package `@xyflow/react`), React Router.
**Backend:** Python 3.11+, FastAPI, Uvicorn, httpx (async HTTP client), Pydantic, pytest, pytest-asyncio (or equivalent) and a mocking library for HTTP (for example `respx`).
**Frontend tests:** Vitest and React Testing Library.

Rules:
- Pick **one** Tailwind major version and stay consistent with its setup instructions.
- Verify every version via npm or pip before pinning (see 1.1).
- Avoid unnecessary dependencies. No paid AI service. No database (in-memory cache only).

---

## 3. Target folder structure

Propose adjustments in Phase 1, but keep this separation of concerns:

```
repo-archaeologist/
├── README.md                  # final user-facing README (Phase 9)
├── README_AGENT.md            # this file
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, routers
│   │   ├── config.py          # env settings
│   │   ├── api/routes.py      # /api/health, /api/analyze
│   │   ├── schemas/           # Pydantic models (the data contract)
│   │   ├── github/
│   │   │   ├── url_parser.py  # strict URL validation
│   │   │   ├── client.py      # GitHub REST client
│   │   │   └── errors.py
│   │   ├── analysis/
│   │   │   ├── languages.py
│   │   │   ├── detectors.py   # package managers, frameworks, config files
│   │   │   ├── entrypoints.py
│   │   │   ├── dependencies.py
│   │   │   ├── filetree.py
│   │   │   ├── graph.py       # import graph + edges
│   │   │   ├── guide.py       # template-based plain-English guide
│   │   │   └── rules.py       # the detection rules table as data
│   │   └── cache.py           # in-memory TTL cache
│   └── tests/
│       ├── fixtures/
│       └── test_*.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind config
    └── src/
        ├── api/               # all network calls
        ├── types/             # TypeScript types matching the schema
        ├── lib/               # url validation, helpers
        ├── components/        # UI components (no fetch calls)
        ├── pages/             # Landing, Analyze
        └── styles/
```

---

## 4. Data contract (build this FIRST, in Phase 1)

Define Pydantic models and matching TypeScript types for `POST /api/analyze`.

**Request:** `{ "url": "https://github.com/owner/repo" }`

**Response (shape; refine in Phase 1):**
```
{
  "repo": {
    "owner", "name", "full_name", "description", "html_url",
    "default_branch", "stars", "forks", "open_issues", "license",
    "primary_language", "topics[]", "size_kb", "pushed_at", "archived"
  },
  "languages": [ { "name", "bytes", "percent" } ],
  "tech_stack": [ Finding ],            // frameworks, package managers, tooling
  "config_files": [ Finding ],
  "entry_points": [ Finding ],          // candidates only
  "dependencies": {
    "ecosystems": [ {
      "ecosystem": "npm|pip|...",
      "manifest_path",
      "runtime": [ { "name", "version_spec", "evidence" } ],
      "dev": [ { "name", "version_spec", "evidence" } ]
    } ]
  },
  "file_tree": {                        // nested or flat with parent ids
    "nodes": [ { "path", "type": "file|dir", "size", "file_kind", "description|null", "github_url" } ],
    "truncated": boolean
  },
  "graph": {
    "nodes": [ { "id", "path", "role", "confidence", "evidence[]" } ],
    "edges": [ { "source", "target", "type": "import|config|dependency", "confidence", "evidence[]" } ],
    "capped": boolean
  },
  "guide": [ { "title", "body", "finding_refs[]" } ],
  "readme": { "found": boolean, "excerpt|null", "html_url|null" },
  "warnings": [ { "code", "message" } ],
  "stats": { "files_in_tree", "files_fetched", "api_calls_made", "analysis_ms" }
}
```

`Finding` = `{ "id", "label", "category", "confidence": "confirmed|heuristic", "summary", "evidence": [ { "path", "reason", "github_url" } ] }`

**Error responses** use a consistent shape: `{ "error": { "code", "message", "retry_after|null" } }` with codes such as `INVALID_URL`, `UNSUPPORTED_HOST`, `NOT_FOUND`, `PRIVATE_OR_FORBIDDEN`, `RATE_LIMITED`, `UPSTREAM_ERROR`, `TIMEOUT`.

The frontend types must be copied from this contract. Do not let the two drift.

---

## 5. GitHub API budget and behavior

Define exact numbers in the Phase 1 plan. Recommended defaults (adjust with justification):

| Item | Recommended |
|---|---|
| Repo metadata | 1 call: `GET /repos/{owner}/{repo}` |
| Languages | 1 call: `GET /repos/{owner}/{repo}/languages` |
| README | 1 call: `GET /repos/{owner}/{repo}/readme` (404 is normal, not an error) |
| Tree | 1 call: `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1` |
| Source/manifest fetches | via `raw.githubusercontent.com`, max ~40 files total |
| Max bytes per file | ~100 KB; skip and warn above this |
| Total byte budget | ~2 MB per analysis |
| Request timeout | ~10 s per call, 1 retry max on network error |
| Cache | in-memory TTL (for example 10 minutes), keyed by `owner/repo@commit-or-branch` |

Required behaviors:
- **Truncated tree:** if the response has `truncated: true`, still analyze what was returned and add a warning `TREE_TRUNCATED`. Do not pretend the tree is complete.
- **Rate limits:** read `X-RateLimit-Remaining` and `X-RateLimit-Reset`. On 403/429 rate limit, return `RATE_LIMITED` with the reset time. Never retry in a tight loop.
- **Private/missing repos:** 404 and 403 map to clear, friendly errors.
- **Unauthenticated limit is 60 requests/hour.** With a token it is much higher. The token is optional.
- **Prioritize fetches:** manifests first (`package.json`, `requirements.txt`, `pyproject.toml`), then entry point candidates, then files near the root, then the rest until the budget runs out. Record skipped files in warnings.
- **Binary and unsupported types:** never fetch images, archives, lockfiles over the size cap, or minified/vendored directories (`node_modules`, `dist`, `build`, `vendor`, `.git`, etc.).

---

## 6. Detection rules (store as data in `rules.py`; document in Phase 1)

Each rule has: `id`, `match`, `finding`, `confidence`, `reason`.

**Package managers and ecosystems**
- `package.json` → npm ecosystem (confirmed). Lockfile decides the manager: `package-lock.json` → npm, `yarn.lock` → Yarn, `pnpm-lock.yaml` → pnpm, `bun.lockb`/`bun.lock` → Bun (all confirmed, file exists).
- `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `setup.cfg` → Python ecosystem. `poetry.lock` → Poetry, `uv.lock` → uv, `Pipfile.lock` → Pipenv.
- Optionally: `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `composer.json`, `Gemfile`. Only add those you can parse and test.

**Frameworks and tools** (confirmed when found in a parsed manifest dependency list; heuristic when only inferred from file names)
- JS/TS: `react`, `next`, `vue`, `nuxt`, `svelte`, `@angular/core`, `vite`, `express`, `nestjs`, `tailwindcss`, `typescript`, `vitest`, `jest`.
- Python: `fastapi`, `flask`, `django`, `pytest`, `numpy`, `pandas`, `torch`, `tensorflow`, `scikit-learn`.
- Config-based: `vite.config.*`, `next.config.*`, `tailwind.config.*`, `tsconfig.json`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/*`, `.eslintrc*`, `pytest.ini`, `Makefile`.

**Entry point candidates** (always label as candidates)
- Confirmed (from manifests): `package.json` fields `main`, `module`, `bin`, and `scripts.start`/`dev`/`build` targets; `pyproject.toml` `[project.scripts]`; `Dockerfile` `CMD`/`ENTRYPOINT`; `Procfile`.
- Heuristic (from naming): `main.py`, `app.py`, `manage.py`, `wsgi.py`, `asgi.py`, `__main__.py`, `index.js/ts`, `main.ts/tsx`, `server.js/ts`, `src/index.*`, `src/main.*`, `src/App.*`, `pages/`/`app/` directories for Next.js.
- Heuristic also applies to `if __name__ == "__main__"` found in a fetched file (that one is confirmed for that file but still not proof it is the primary entry point; explain this in the evidence reason).

**File classification** by extension/name: source, test, config, docs, asset, data, build output, CI, lockfile. Only add short descriptions for well-known files (for example `package.json`, `Dockerfile`, `.gitignore`, `README.md`). Otherwise `description: null`.

---

## 7. Graph inference rules

**Node roles:** `entry`, `source`, `config`, `test`, `docs`, `dependency_group`.

**Edge types (must be visually and semantically distinct):**
1. `import` (confirmed): parsed from fetched source files and resolved to another file in the repo tree.
2. `config` (confirmed or heuristic, state which): a config or manifest references a file (for example `package.json` `main`, `vite.config` referencing an entry, `Dockerfile` copying/running a file).
3. `dependency` (confirmed that it is declared, **not** proven used): manifest to dependency group. Label it **"declared, not proven used"**.

**Parsing:**
- Python: use the standard `ast` module. Handle `import x`, `from x import y`, and relative imports. Wrap parsing in try/except for syntax errors and add a warning.
- JS/TS: lightweight parsing of `import ... from '...'`, `export ... from '...'`, `require('...')`, and static `import('...')`. Regex is acceptable if tested with fixtures. Document limits.
- Resolve only **relative and clearly local imports** to files in the tree (try extensions and `index` files). If it cannot be resolved with certainty, **skip it and add a warning**. Do not guess.
- Known limits to document: path aliases (`@/`), dynamic imports, monorepo workspaces, generated code, runtime-only dependencies.
- Handle circular imports without infinite loops.
- Cap nodes (propose a number, for example 150) and set `capped: true` when exceeded.

---

## 8. Design system and UI direction

**Goal:** an interface that looks designed by a person with taste, not generated from a template. It must feel like a precision instrument for reading code, comparable in seriousness to tools such as a debugger, a profiler or a terminal-based inspector.

### 8.1 Concept: "The Survey Sheet"
The repository is an **excavation site**. The UI borrows from archaeological and surveying documents, applied with restraint (no cartoon shovels or sand textures):
- Folders are **strata**: depth is shown with a depth rail and indentation ticks.
- Findings are **catalogued artifacts** with catalog IDs (`ART-001`, `ART-002`, ...).
- Confidence is a **provenance stamp**: confirmed vs heuristic (see 8.3).
- Layout feels like a **survey sheet**: hairline rules, tick marks on edges, labeled coordinates, key-value tables.
- Voice is **dry, precise, field-notes style**. Never hype.

### 8.2 Color tokens (define once as CSS variables / Tailwind theme)
Suggested starting values (tune by eye, but keep the semantic rules):

| Token | Value | Use |
|---|---|---|
| `--bg-0` | `#07080A` | app background |
| `--bg-1` | `#0C0E12` | panels |
| `--bg-2` | `#12151B` | raised rows, inputs |
| `--line` | `#1D222B` | hairline borders |
| `--line-strong` | `#2A313D` | active borders |
| `--text-0` | `#E7EAEE` | primary text |
| `--text-1` | `#9AA3AF` | secondary text |
| `--text-2` | `#646C78` | tertiary, non-essential only |
| `--cyan` | `#4FD8EB` | **confirmed** facts, primary action, focus |
| `--violet` | `#9D8CFF` | **heuristic** findings, secondary accent |
| `--amber` | `#E8B964` | warnings, partial results |
| `--red` | `#F26B6B` | errors |

**Rule: color carries meaning.** Cyan means confirmed or primary action. Violet means heuristic. Amber means warning. Red means error. Do not use accent colors decoratively. Check text contrast (WCAG AA) for every text/background pair.

### 8.3 Signature elements (implement these; they are what make it distinctive)
1. **Strata hero background:** subtle horizontal layered bands (CSS or inline SVG) with fine tick marks and coordinate labels along the edges. No gradient blobs, no glow orbs.
2. **Provenance stamps:**
   - `CONFIRMED`: solid thin cyan outline, small filled dot, uppercase mono label.
   - `HEURISTIC`: **dashed** violet outline, hollow dot, uppercase mono label.
   - Tooltip explains the difference in one sentence.
3. **Artifact cards for findings:** catalog ID, label, one-line summary, stamp, and an "evidence" toggle. Use rows and hairlines, not heavy boxed cards.
4. **Evidence drawer:** slide-in panel showing monospaced file path, the reason, and a "View on GitHub" link. Show a code snippet only if it came from content actually fetched; never fabricate snippets.
5. **Honest excavation log (loading state):** terminal-style log with real stage labels (for example "Fetching repository metadata", "Reading file tree", "Parsing manifests"). Progress must reflect **real** backend progress (propose Server-Sent Events or a polling status in Phase 1), or be an honest indeterminate indicator. **No fake progress percentages.**
6. **Depth rail in the file explorer:** vertical guide lines per nesting level, file-kind glyphs, match highlighting for search, keyboard navigation.
7. **Survey-style overview:** repo facts as a compact key-value table (owner, branch, size, last push, license, languages) plus a thin segmented language bar. Avoid a grid of identical stat cards.
8. **Graph canvas:** dark canvas with a dotted grid, compact rectangular nodes with a mono label and a colored left edge by role, edges styled by type (solid = import, dashed = config, dotted = declared dependency), legend panel, minimap.
9. **Keyboard affordances:** `/` focuses file search, `Esc` closes the drawer, visible focus rings everywhere.
10. **Optional stretch (only after everything else works):** `Ctrl+K` command palette to jump to sections or files.

### 8.4 Typography
- Mono-forward interface. Mono for paths, IDs, labels, stamps, numbers. A clean, characterful sans for body text.
- Suggested pairing: **Geist** (or IBM Plex Sans) for UI and **JetBrains Mono** (or Geist Mono) for code. Self-host via `@fontsource` packages (verify exact package names and versions with `npm view` before installing). **Do not load fonts from a CDN.**
- Define a type scale (for example 11, 12, 13, 14, 16, 20, 28, 44, 64 px). Headlines: large, tight letter-spacing, medium weight. Small labels: uppercase mono with wide letter-spacing.
- Never use more than two font families.

### 8.5 Layout and shape
- Strong grid, asymmetric composition. Not a centered stack of equal sections.
- Dense but readable: hairline separators instead of boxes around everything.
- Radius small (2 to 6 px). Almost no shadows; use border color and a subtle accent ring for focus and active state.
- Consistent spacing scale (4 px base). Generous whitespace around the hero and between dashboard sections.
- Sticky top bar with repo identity on the dashboard. Sticky left section rail on desktop; becomes a horizontal tab bar or bottom sheet on mobile.

### 8.6 Landing page specification
- **Top bar:** logo mark (simple, geometric, drawn as SVG, no stock icon), product name, nav (How it works, Examples, GitHub), small "Public repos only" note.
- **Hero (left-aligned, asymmetric):**
  - Headline (suggested): "Read a codebase like a site survey."
  - Subline (suggested): "Paste a public GitHub URL. Get the structure, dependencies and likely entry points, each with the evidence behind it."
  - Large mono URL input with a leading `github.com/` affordance, inline validation message area, and the **Analyze Repository** button. Enter key submits.
  - Beside or behind the input: the strata background with a small, **static, clearly labeled sample** of an artifact card. Label it "Example output" so it is not mistaken for real analysis.
- **Examples row:** chips for real public repos (verify each exists via the API before listing).
- **Feature overview:** four items laid out as a numbered list or table (`01 Structure`, `02 Dependencies`, `03 Entry points`, `04 Architecture graph`), each one sentence. Not three identical icon cards.
- **"Confirmed vs heuristic" explainer:** short section showing the two stamps and what they mean. This is the product's honesty feature; make it visible.
- **Footer:** GitHub links, project info, "Deterministic analysis, no AI model", public-repos-only note.

### 8.7 Dashboard specification (`/analyze`)
Sections, in order, each with an anchor in the left rail:
1. **Overview** (survey sheet table, language bar, README status)
2. **Technology stack** (artifact rows with stamps)
3. **Structure** (searchable explorer with depth rail; file count and truncation notice)
4. **Entry point candidates** (artifact rows with evidence drawer)
5. **Dependencies** (per ecosystem, runtime vs dev, labeled "declared in manifest")
6. **Architecture** (graph with legend, filters, inspector)
7. **Guide** (plain-English sections; each section lists which artifacts it came from)

Include: warnings banner (amber), error states (red, with retry), empty states with a one-line explanation of why it is empty, skeletons that match final layout.

### 8.8 Motion
- 120 to 200 ms, ease-out. One subtle scan-line or reveal on first load. Hover and focus transitions only otherwise.
- Respect `prefers-reduced-motion` (disable the scan effect and transitions).
- No bouncing, no parallax gimmicks, no looping decorative animation.

### 8.9 Banned patterns (the "AI-template" list)
Do **not** use any of the following:
- Purple-to-blue gradients, gradient text, glowing blobs, aurora backgrounds
- Glassmorphism used everywhere, heavy blur, neon glow borders
- Centered hero with a giant gradient headline and two buttons
- Three or more identical feature cards with an icon in a tinted square
- Emoji as icons or decoration
- Words like "supercharge", "unlock", "seamless", "revolutionize", "next-gen", "AI-powered"
- Fake testimonials, fake statistics, fake company logos, fake "trusted by"
- Lorem ipsum or placeholder text of any kind in the final UI
- Stock illustrations, 3D blobs, generic isometric art
- `rounded-2xl` on everything, big soft shadows, pill buttons everywhere
- Equal visual weight for every element (there must be a clear hierarchy)

### 8.10 Design process (required, in this order)
1. Write `frontend/DESIGN_BRIEF.md`: tokens, type scale, spacing, component inventory, and how each signature element in 8.3 will be built.
2. Build a `/styleguide` route showing tokens, type scale, stamps, artifact card, buttons, inputs, explorer row, drawer, banner, skeleton. **Stop for my approval** before building pages.
3. Build the landing page. Screenshot at 1440 px and 390 px.
4. **Self-critique:** compare the screenshots against 8.9 and list every violation honestly, then fix them and re-screenshot.
5. After the dashboard and graph, repeat steps 3 and 4.

### 8.11 Accessibility and responsiveness
Works from 390 px to 1440 px and beyond. Keyboard-only usable. Visible focus ring in cyan. `aria-live` regions for loading and errors. Do not rely on color alone: stamps differ by outline style and label as well as color. Graph has a list-view alternative.

---

## 9. Phases

**Process for every phase:**
1. Re-read sections 1 (rules) and the relevant sections of this file.
2. Write a short plan for the phase and wait for my approval **only in Phase 1**; in other phases, proceed after stating your plan.
3. Implement.
4. Run the verification commands listed. Paste real output.
5. Write the phase report using the template in section 11.
6. **Stop.** Do not begin the next phase.

---

### Phase 0: Workspace rules and hygiene
**Steps**
1. Read this entire file.
2. Create the workspace rules file for the agent (use the Antigravity rules mechanism) summarizing section 1.
3. Create `.gitignore` (Python: `__pycache__`, `.venv`, `.pytest_cache`; Node: `node_modules`, `dist`; env: `.env`, `.env.*` except `.env.example`; OS/editor files).
4. Check the workspace with `git status`. If it is not a git repo, tell me; do not init unless asked.
5. Do **not** write application code.

**Verify:** list created files and show `.gitignore` contents.

---

### Phase 1: Plan and data contract (no application code)
**Steps**
1. Inspect the workspace and tool versions: `python --version`, `node --version`, `npm --version`. Report actual output.
2. Produce an implementation plan covering: folder structure; the full JSON schema (section 4); GitHub API budget with real numbers (section 5); detection rules table (section 6); graph inference rules and limits (section 7); test plan; risk list.
3. Look up and report real versions for every package via `npm view` / `pip index versions`. Choose one Tailwind major version and justify it.
4. Write the Pydantic models and TypeScript types to files so the contract is concrete.
5. Make one real, unauthenticated call to the GitHub API for a small public repo and paste a **trimmed** real response to confirm field names you rely on (repo metadata, tree, languages).
6. List open questions and assumptions.

**Verify:** I review the plan. **Stop and wait for approval.**

---

### Phase 2: Backend foundation
**Steps**
1. Create the venv instructions (do not commit the venv) and `requirements.txt` with verified pinned versions.
2. `config.py`: settings from environment (`GITHUB_TOKEN` optional, `ALLOWED_ORIGINS`, cache TTL, budgets). Provide `.env.example` with placeholders.
3. `url_parser.py`: strict validation.
   - Accept: `https://github.com/owner/repo`, with optional trailing slash, optional `.git`.
   - Reject: non-https schemes, hosts other than exactly `github.com` (including `www.github.com` unless the plan explicitly normalizes it, `github.com.evil.com`, `evilgithub.com`, `gist.github.com`), userinfo (`user@`), ports, IP hosts, percent-encoded tricks, whitespace and control characters, empty owner/repo, invalid owner/repo characters, paths with extra segments (decide in plan: reject or normalize `/tree/branch`), overly long input.
4. `client.py`: async GitHub client with timeouts. Methods: get repo, get languages, get README (404 handled), get tree (handle `truncated`), fetch raw file with byte limit (stream and stop at limit). Map errors to typed exceptions: not found, forbidden/private, rate limited (include reset time), timeout, upstream error. Never log the token.
5. `main.py`: FastAPI app, CORS limited to localhost dev origins, `GET /api/health` returning `{status, github_token_configured}` only (see 1.4). Add token-redaction in logging and a test proving a fake token never appears in responses or logs.
6. Tests with pytest:
   - URL validator: at least 20 cases, including at least 10 malicious or malformed.
   - Client with mocked HTTP: success, 404, 403 private, 403/429 rate limit with headers, timeout, truncated tree, oversized file.

**Verify (paste real output):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload --port 8000
# in another terminal:
Invoke-RestMethod http://localhost:8000/api/health
```

---

### Phase 3: Analysis engine (no network in tests)
**Steps**
1. Implement analysis modules from section 3 as pure functions that take already-fetched data (tree, manifest contents) and return findings. They must not make network calls.
2. Languages: from the API language bytes (confirmed) with extension-based fallback (heuristic).
3. Detectors: package managers, frameworks, config files using `rules.py`.
4. Entry points: per section 6, each with evidence.
5. Dependencies: parse `package.json`, `requirements.txt` (handle comments, extras, version markers, `-r` includes, URLs, editable installs without crashing), `pyproject.toml` (use `tomllib` on Python 3.11+). Handle malformed files gracefully with a warning.
6. File tree builder: nested structure, classification, short descriptions only for well-known files.
7. Guide generator: template sentences filled from findings. Each guide section lists `finding_refs`. No filler text.
8. Create fixtures in `backend/tests/fixtures/` (realistic fake trees and manifests): Python FastAPI app, Vite React TS app, Next.js app, plain Python script repo, empty repo, repo with no README, repo with malformed `package.json`.
9. Write tests for every rule, including negative tests (things that must **not** be detected).

**Verify:** paste `pytest -v` output. List any rule that is not covered by a test.

---

### Phase 4: Import graph and `/api/analyze`
**Steps**
1. Implement the file selection strategy from section 5 (prioritized, budgeted).
2. Implement graph building from section 7 (Python via `ast`, JS/TS via parser/regex).
3. Implement `POST /api/analyze`: validate, check cache, fetch metadata/languages/README/tree, run analysis, assemble the response matching the schema exactly, populate `warnings` and `stats`.
4. In-memory TTL cache with a size limit.
5. Graceful partial results: rate limit mid-analysis, truncated tree, skipped large files, unparsable files.
6. Tests: graph building (normal, circular imports, unresolved imports, syntax errors), endpoint tests with the GitHub client mocked, error mapping tests.

**Verify (paste real results):**
```powershell
pytest -v
# start server, then test against real repos (use a token if rate limited)
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/analyze -ContentType "application/json" -Body '{"url":"https://github.com/<small-python-repo>"}'
```
Test one small Python repo, one small JS/TS repo, and one large repo (for example `facebook/react`). For each, report status, timing, number of nodes/edges/warnings, and the entry points found. If rate limited, say so.

---

### Phase 5: Frontend scaffold and landing page
**Steps**
1. Scaffold Vite + React + TS. Install pinned verified versions (Tailwind, `lucide-react`, `react-router-dom`, `@xyflow/react`, self-hosted font packages).
2. Follow section 8.10 exactly: write `DESIGN_BRIEF.md`, set up design tokens, build the `/styleguide` route, then **stop and wait for my approval** before building the landing page.
3. `src/lib/validateRepoUrl.ts` mirroring backend rules, with unit tests (Vitest).
4. `src/api/` client with typed functions and error mapping. **No fetch in components.**
5. `src/types/` copied from the approved schema.
6. Router: `/` landing, `/analyze?repo=owner/repo` results.
7. Landing page per section 8. Input validates on change/submit with clear inline messages.
8. Configure Vite dev proxy or env-based API base URL (`VITE_API_BASE_URL`). No secrets in `VITE_` variables.

**Verify (paste real output):**
```powershell
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```
Open the app in the browser. Capture screenshots at 1440 px and 390 px. List layout bugs found and fix them. Say honestly if you could not capture screenshots.

---

### Phase 6: Results dashboard
**Steps**
1. `/analyze` page calls the real backend.
2. Loading state with progress steps and skeletons. Handle cancellation when the user navigates away.
3. Error states for each error code: invalid URL, unsupported host, not found, private, rate limited (show reset time), network failure, timeout. Include a retry action where sensible.
4. Warnings banner for partial results.
5. Components: overview cards, tech stack, file explorer (collapsible folders, search/filter, file-type icons, descriptions where available, GitHub link per file), entry point candidates (evidence list and confirmed/heuristic badge), dependency overview (per ecosystem, runtime vs dev, labeled "declared in manifest"), plain-English guide, README section with empty state.
6. Empty states: no README, no dependencies, no entry points, empty repository.
7. Responsive layout 390 px to 1440 px.

**Verify:** run against three real repos, one repo with no README, one nonexistent repo, and one malformed URL. Report every bug found and how it was fixed. Paste build/lint/test output.

---

### Phase 7: Architecture graph
**Steps**
1. Use `@xyflow/react` with real graph data from the backend.
2. Custom node styles by role. Distinct edge styles per type (solid, dashed, dotted) plus a **legend**.
3. Auto-layout (choose a lightweight approach; verify any layout library via npm before adding it).
4. Click a node to open an inspector panel: path, role, confidence badge, evidence list, GitHub link.
5. Filters by edge type and node role. Zoom, pan, minimap, fit-view.
6. Respect the backend `capped` flag. Add a "show more" control if you cap on the client.
7. Label dependency edges clearly as "declared, not proven used".
8. Keyboard accessibility and a text alternative (for example a list view toggle).

**Verify:** test with a small repo and with `facebook/react`. Report whether it stays responsive and how many nodes rendered. Paste build output. Click several nodes and confirm evidence matches the GitHub file.

---

### Phase 8: Hardening and QA
**Steps**
1. **Security review:** only `api.github.com` and `raw.githubusercontent.com` contacted; no user-supplied URLs fetched; token absent from responses, logs, and frontend bundle (grep `dist/` for the token and for `GITHUB_TOKEN`); CORS not wildcard; input length limits; dependency audit (`npm audit`, `pip-audit` if available).
2. **Robustness:** rate limits, timeouts, truncated trees, private/missing repos, huge files, binary files, malformed manifests, empty repos.
3. **Accessibility:** labels, focus order, contrast (check every token pair), reduced motion.
3b. **Design review:** compare every page against section 8.9 (banned patterns) and 8.3 (signature elements). List violations honestly and fix them. Provide screenshots at 1440 px and 390 px.
3c. **Token check:** grep `dist/` and the repo for `ghp_` and `github_pat_` and paste the real result; run `git check-ignore -v backend/.env`.
4. **Tests:** add Vitest tests for URL validation and at least two key components (for example the file explorer search and the evidence/badge component).
5. Fix what you find. List what you could not fix.

**Verify:** paste the full output of all backend tests, all frontend tests, lint, and production build.

---

### Phase 9: Documentation and final report
**Steps**
1. Write the user-facing `README.md` with: overview, features, how it works (deterministic rules, not AI), architecture diagram (text or Mermaid), confirmed vs heuristic explanation, setup, configuration (`.env`), limitations, security notes, project structure, testing, screenshots placeholders (`docs/screenshots/*.png`), and license placeholder.
2. Include **Windows PowerShell** commands:
```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# optional: edit .env and set GITHUB_TOKEN (read-only public access, no scopes)
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Tests
cd backend; pytest -v
cd frontend; npm run test
```
If script execution is blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
3. Follow the README commands literally and report what worked and what did not.
4. Produce the final report (section 11).

Do not push or deploy.

---

## 10. Definition of done

The project is done only when **all** of these are true and demonstrated with real output:
- [ ] Backend tests pass (output shown).
- [ ] Frontend tests, lint, and production build pass (output shown).
- [ ] Both servers start with the documented PowerShell commands.
- [ ] Analysis works on at least: one small Python repo, one small JS/TS repo, one Next.js or Vite repo, one large repo.
- [ ] Invalid URLs, unsupported hosts, missing repos, private repos, rate limits, and network failures show friendly errors.
- [ ] A repo with no README renders correctly.
- [ ] Every finding shows confidence and evidence with a working GitHub link.
- [ ] The graph distinguishes import, config, and dependency edges, and has a legend.
- [ ] No token or secret appears anywhere in frontend code or the built bundle.
- [ ] `.env.example` exists with placeholders only; `backend/.env` is git-ignored (proof shown); token not found in `dist/` or repo.
- [ ] `/api/health` reports `github_token_configured` without revealing the token.
- [ ] UI passes the design review in 8.9 with screenshots, and all signature elements in 8.3 (except the optional stretch) are present.
- [ ] README is complete and its commands were verified.
- [ ] Nothing was pushed or deployed.
- [ ] Known limitations are listed honestly.

---

## 11. Report template (use at the end of EVERY phase)

```
## Phase N report

### What I did
(short summary)

### Files created or changed
(list with paths)

### Commands run and real output
(paste the actual output, trimmed only where noted)

### Verified working
(only things demonstrated by output above)

### NOT RUN / Not done / Problems
(be explicit: skipped steps, failures, uncertainties, assumptions)

### Questions for me
(if any)

### Ready for the next phase?  yes / no, and why
```

---

## 12. Known limitations to state in the final README

- Deterministic rules only; no AI explanations; descriptions exist only for well-known files.
- Entry points are candidates, not proof of execution flow.
- Dependencies are declared, not proven used.
- Import graph covers a limited number of files within the byte and file budget.
- Path aliases, dynamic imports, monorepo workspaces, and generated code are not fully resolved.
- Unauthenticated GitHub API access allows roughly 60 requests per hour; large repos may produce partial results.
- Truncated trees for very large repositories produce partial results with a warning.
- Public repositories only.
- Languages beyond Python and JS/TS get structure and manifest analysis, but no import graph.

---

## 13. If you get stuck or make a mistake

- Stop, explain the problem plainly, and propose options. Do not paper over errors.
- If earlier work you reported as passing is now failing, say so and re-run it.
- If a package or API does not behave as expected, check the real docs or actual response; do not guess.
