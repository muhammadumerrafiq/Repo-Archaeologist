import pytest
import respx
import httpx
from app.github.client import GitHubClient
from app.github.errors import (
    RepoNotFoundError,
    RepoPrivateOrForbiddenError,
    RateLimitExceededError,
    GitHubTimeoutError,
    UpstreamGitHubError,
)

@pytest.mark.asyncio
class TestGitHubClient:
    """Mocked HTTP tests for GitHub API client."""

    @respx.mock
    async def test_get_repo_success(self):
        respx.get("https://api.github.com/repos/pallets/click").respond(
            200,
            json={"name": "click", "full_name": "pallets/click", "stargazers_count": 15000}
        )
        async with GitHubClient() as client:
            repo = await client.get_repo("pallets", "click")
            assert repo["name"] == "click"
            assert repo["stargazers_count"] == 15000

    @respx.mock
    async def test_get_repo_404_not_found(self):
        respx.get("https://api.github.com/repos/nonexistent/repo").respond(404)
        async with GitHubClient() as client:
            with pytest.raises(RepoNotFoundError) as exc_info:
                await client.get_repo("nonexistent", "repo")
            assert "not found" in str(exc_info.value).lower()

    @respx.mock
    async def test_get_repo_403_private_or_forbidden(self):
        respx.get("https://api.github.com/repos/secret/internal").respond(
            403,
            headers={"x-ratelimit-remaining": "50"},
            json={"message": "Must have admin rights"}
        )
        async with GitHubClient() as client:
            with pytest.raises(RepoPrivateOrForbiddenError) as exc_info:
                await client.get_repo("secret", "internal")
            assert "forbidden" in str(exc_info.value).lower()

    @respx.mock
    async def test_get_repo_rate_limited(self):
        respx.get("https://api.github.com/repos/heavy/traffic").respond(
            403,
            headers={
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": "1893456000",
            },
            json={"message": "API rate limit exceeded"}
        )
        async with GitHubClient() as client:
            with pytest.raises(RateLimitExceededError) as exc_info:
                await client.get_repo("heavy", "traffic")
            assert exc_info.value.code == "RATE_LIMITED"
            assert exc_info.value.retry_after is not None

    @respx.mock
    async def test_get_languages_success(self):
        respx.get("https://api.github.com/repos/tiangolo/fastapi/languages").respond(
            200,
            json={"Python": 95000, "Shell": 5000}
        )
        async with GitHubClient() as client:
            langs = await client.get_languages("tiangolo", "fastapi")
            assert langs["Python"] == 95000

    @respx.mock
    async def test_get_readme_found(self):
        respx.get("https://api.github.com/repos/owner/repo/readme").respond(
            200,
            json={"name": "README.md", "content": "IyBTYW1wbGU=", "encoding": "base64"}
        )
        async with GitHubClient() as client:
            readme = await client.get_readme("owner", "repo")
            assert readme is not None
            assert readme["name"] == "README.md"

    @respx.mock
    async def test_get_readme_404_handled_gracefully(self):
        respx.get("https://api.github.com/repos/owner/noreadme/readme").respond(404)
        async with GitHubClient() as client:
            readme = await client.get_readme("owner", "noreadme")
            assert readme is None

    @respx.mock
    async def test_get_tree_truncated_flag(self):
        respx.get("https://api.github.com/repos/huge/repo/git/trees/main?recursive=1").respond(
            200,
            json={
                "sha": "abc1234",
                "truncated": True,
                "tree": [{"path": "file1.py", "type": "blob", "size": 100}]
            }
        )
        async with GitHubClient() as client:
            tree = await client.get_tree("huge", "repo", "main")
            assert tree["truncated"] is True
            assert len(tree["tree"]) == 1

    @respx.mock
    async def test_get_repo_timeout(self):
        respx.get("https://api.github.com/repos/slow/repo").mock(
            side_effect=httpx.TimeoutException("Connection timed out")
        )
        async with GitHubClient(timeout=0.1) as client:
            with pytest.raises(GitHubTimeoutError):
                await client.get_repo("slow", "repo")

    @respx.mock
    async def test_fetch_raw_file_normal(self):
        content = "console.log('Hello Archaeologist!');"
        respx.get("https://raw.githubusercontent.com/owner/repo/main/index.js").respond(
            200,
            content=content.encode("utf-8")
        )
        async with GitHubClient() as client:
            text, truncated = await client.fetch_raw_file("owner", "repo", "main", "index.js")
            assert truncated is False
            assert text == content

    @respx.mock
    async def test_fetch_raw_file_oversized(self):
        # 120 KB content exceeds 100 KB limit
        oversized_bytes = b"X" * (120 * 1024)
        respx.get("https://raw.githubusercontent.com/owner/repo/main/bundle.js").respond(
            200,
            content=oversized_bytes
        )
        async with GitHubClient() as client:
            text, truncated = await client.fetch_raw_file(
                "owner", "repo", "main", "bundle.js", max_bytes=100 * 1024
            )
            assert truncated is True
            assert text is None
