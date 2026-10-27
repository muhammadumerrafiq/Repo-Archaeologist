import pytest
import respx
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.cache import analysis_cache

@pytest.mark.asyncio
class TestApiAnalyzeEndpoint:
    """End-to-end integration tests for POST /api/analyze."""

    def setup_method(self):
        analysis_cache.clear()

    @respx.mock
    async def test_analyze_success(self):
        owner, repo = "sampleorg", "sample-repo"

        # Mock GitHub endpoints
        respx.get(f"https://api.github.com/repos/{owner}/{repo}").respond(
            200,
            json={
                "id": 12345,
                "name": repo,
                "full_name": f"{owner}/{repo}",
                "description": "A sample repository",
                "html_url": f"https://github.com/{owner}/{repo}",
                "default_branch": "main",
                "stargazers_count": 50,
                "forks_count": 10,
                "open_issues_count": 1,
                "license": {"name": "MIT License"},
                "language": "Python",
                "topics": ["sample"],
                "size": 120,
                "pushed_at": "2026-03-01T12:00:00Z",
                "archived": False,
            }
        )
        respx.get(f"https://api.github.com/repos/{owner}/{repo}/languages").respond(
            200,
            json={"Python": 45000}
        )
        respx.get(f"https://api.github.com/repos/{owner}/{repo}/readme").respond(
            200,
            json={
                "html_url": f"https://github.com/{owner}/{repo}/blob/main/README.md",
                "content": "IyBTYW1wbGUgUmVwb3NpdG9yeQpUaGlzIGlzIGEgdGVzdC4=" # Base64 for "# Sample Repository\nThis is a test."
            }
        )
        respx.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1").respond(
            200,
            json={
                "sha": "tree123",
                "truncated": False,
                "tree": [
                    {"path": "requirements.txt", "type": "blob", "size": 30},
                    {"path": "main.py", "type": "blob", "size": 120},
                    {"path": "README.md", "type": "blob", "size": 50},
                ]
            }
        )
        respx.get(f"https://raw.githubusercontent.com/{owner}/{repo}/main/requirements.txt").respond(
            200,
            content=b"fastapi==0.100.0\npytest>=7.0\n"
        )
        respx.get(f"https://raw.githubusercontent.com/{owner}/{repo}/main/main.py").respond(
            200,
            content=b"import os\nif __name__ == '__main__':\n    print('Hello')\n"
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/analyze",
                json={"url": f"https://github.com/{owner}/{repo}"}
            )
            assert resp.status_code == 200
            data = resp.json()

            # Verify response schema fields
            assert data["repo"]["name"] == repo
            assert data["repo"]["owner"] == owner
            assert len(data["languages"]) == 1
            assert data["languages"][0]["name"] == "Python"

            # Tech stack findings
            tech_labels = [f["label"] for f in data["tech_stack"]]
            assert "Python" in tech_labels
            assert "FastAPI" in tech_labels
            assert "Pytest" in tech_labels

            # Dependencies
            ecosystems = data["dependencies"]["ecosystems"]
            assert len(ecosystems) == 1
            assert ecosystems[0]["ecosystem"] == "pip"
            runtime_dep_names = [d["name"] for d in ecosystems[0]["runtime"]]
            assert "fastapi" in runtime_dep_names

            # Tree & Graph
            assert len(data["file_tree"]["nodes"]) == 3
            assert len(data["graph"]["nodes"]) >= 1

            # Guide
            assert len(data["guide"]) >= 2
            assert all(len(s["finding_refs"]) > 0 for s in data["guide"])

            # README
            assert data["readme"]["found"] is True
            assert "Sample Repository" in data["readme"]["excerpt"]

            # Stats
            assert data["stats"]["files_in_tree"] == 3
            assert data["stats"]["files_fetched"] >= 2
            assert data["stats"]["api_calls_made"] == 4

            # Verify Cache Hit on subsequent request
            resp2 = await client.post(
                "/api/analyze",
                json={"url": f"https://github.com/{owner}/{repo}"}
            )
            assert resp2.status_code == 200

    @respx.mock
    async def test_analyze_404_not_found(self):
        respx.get("https://api.github.com/repos/unknown/missing").respond(404)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/analyze",
                json={"url": "https://github.com/unknown/missing"}
            )
            assert resp.status_code == 404
            err = resp.json()
            assert err["error"]["code"] == "NOT_FOUND"

    async def test_analyze_invalid_url(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/analyze",
                json={"url": "http://evil.com/owner/repo"}
            )
            assert resp.status_code == 400
            err = resp.json()
            assert err["error"]["code"] in ("INVALID_URL", "UNSUPPORTED_HOST")

    @respx.mock
    async def test_analyze_rate_limited(self):
        respx.get("https://api.github.com/repos/busy/repo").respond(
            403,
            headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1893456000"},
            json={"message": "API rate limit exceeded"}
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/analyze",
                json={"url": "https://github.com/busy/repo"}
            )
            assert resp.status_code == 429
            err = resp.json()
            assert err["error"]["code"] == "RATE_LIMITED"
            assert err["error"]["retry_after"] is not None
