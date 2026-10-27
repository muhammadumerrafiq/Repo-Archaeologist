# Repo Archaeologist - Workspace Rules & Constraints

These rules are non-negotiable and govern all work on this project (derived from `README_AGENT.md` Section 1).

## 1. Honesty Protocol (Anti-Hallucination)
1. **Never claim a test, build, lint, or command passed unless you ran it in this session and can paste the real output.** If not run, write "NOT RUN".
2. **Never invent package names or versions.** Before pinning any dependency, verify it:
   - npm: `npm view <package> version`
   - pip: `pip index versions <package>`
3. **Never invent GitHub API endpoints or response fields.** Use only fields observed in a real API response or official GitHub REST docs (`https://docs.github.com/en/rest`).
4. **Never fabricate analysis results, sample outputs, or screenshots.** If rate limited, say so and stop. Do not simulate data.
5. **Never use mock data in the final application.** Fixtures are allowed only inside tests.
6. If something fails, is skipped, or is uncertain, list it under **"Not done / Problems"** in your report. Reporting problems is success. Hiding them is failure.
7. If a requirement is ambiguous, state your assumption explicitly in the plan instead of silently choosing.
8. Do not add features that are not in `README_AGENT.md`.

## 2. Safety Rules
1. **Never execute, install, import, or run code from analyzed repositories.** Analysis is strictly read-only text parsing.
2. **Only public repositories.** Never request write permissions or OAuth scopes.
3. **The GitHub token (optional) lives only in the backend environment variable `GITHUB_TOKEN`.** It must never appear in frontend code, API responses, logs, error messages, or the built frontend bundle.
4. **Never commit real credentials.** Provide `.env.example` with placeholders only. `.env` must be in `.gitignore`.
5. **SSRF protection:** the backend may only contact `api.github.com` and `raw.githubusercontent.com`. User input is never used as a free-form URL for requests.
6. **No `git push`, no deployment, no publishing packages.** Local commits only, and only if explicitly asked.
7. **CORS:** allows only `http://localhost:5173` and `http://127.0.0.1:5173` (configurable via env). No wildcard.

## 3. Analysis Integrity Rules
1. Use **deterministic rules** only. Do NOT claim AI-generated explanations. The UI and README must not say "AI-powered".
2. Every finding carries:
   - `label`: human-readable name
   - `confidence`: `"confirmed"` or `"heuristic"`
   - `evidence[]`: each item has `path`, `reason`, and `github_url`
3. **Confirmed** means directly observable fact (e.g. `package.json` exists and lists `vite` under `devDependencies`; parsed import resolves to repo file).
4. **Heuristic** means inferred from naming or convention (e.g. `src/main.tsx` is likely an entry point).
5. Never state that a dependency is "used". Say **"declared in manifest"**.
6. Never claim every detected file is an execution entry point. Call them **"entry point candidates"**.
7. Every sentence in the plain-English guide must trace to a finding. No invented descriptions.

## 4. GitHub Token Rules
1. Read only from environment variable `GITHUB_TOKEN` in backend `config.py`. Send only as `Authorization` header to `api.github.com`.
2. **Never open, print, echo, `cat`, log, or quote the contents of `backend/.env`.**
3. `.env` must be git-ignored.
4. `GET /api/health` returns `{ "status": "ok", "github_token_configured": true|false }`. Never return the token, a prefix, or its length.
5. Redact `Authorization` headers from all logs, error messages, and exception traces.
6. Add a test proving the token string never appears in any API response or log output.
7. Phase 8 must grep the built frontend (`dist/`) and repository for token-like strings (`ghp_`, `github_pat_`).
8. If the app runs without a token, it must still work with a visible warning about the lower rate limit.

## 5. Repository Documentation & Sync Protocol
1. Every time changes are pushed to GitHub, ensure root `README.md` and the GitHub repository 'About' metadata (description and topics) are kept up-to-date and reflect recent phases, features, and screenshots.
