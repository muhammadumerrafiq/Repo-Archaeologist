import time
import httpx
from typing import Dict, Any, Optional, Tuple
from ..config import settings
from .errors import (
    GitHubError,
    RepoNotFoundError,
    RepoPrivateOrForbiddenError,
    RateLimitExceededError,
    UpstreamGitHubError,
    GitHubTimeoutError,
)

class GitHubClient:
    """
    Async GitHub API client enforcing strict SSRF isolation,
    rate-limit handling, token redaction, and file-byte budgeting.
    """

    API_BASE = "https://api.github.com"
    RAW_BASE = "https://raw.githubusercontent.com"

    def __init__(self, token: Optional[str] = None, timeout: float = 10.0):
        self.token = token or settings.GITHUB_TOKEN
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        headers = {
            "User-Agent": "Repo-Archaeologist-Engine",
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token and self.token.strip():
            headers["Authorization"] = f"Bearer {self.token.strip()}"

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(self.timeout, connect=5.0),
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    def _get_rate_limit_reset(self, response: httpx.Response) -> Optional[int]:
        reset_header = response.headers.get("x-ratelimit-reset")
        if reset_header and reset_header.isdigit():
            reset_ts = int(reset_header)
            now = int(time.time())
            return max(0, reset_ts - now)
        retry_after = response.headers.get("retry-after")
        if retry_after and retry_after.isdigit():
            return int(retry_after)
        return None

    def _handle_response_status(self, response: httpx.Response, resource_desc: str):
        if response.status_code == 200:
            return

        remaining = response.headers.get("x-ratelimit-remaining")
        reset_seconds = self._get_rate_limit_reset(response)

        if response.status_code in (403, 429):
            if remaining == "0" or "rate limit" in response.text.lower():
                raise RateLimitExceededError(
                    f"GitHub API rate limit reached while accessing {resource_desc}.",
                    retry_after=reset_seconds
                )
            raise RepoPrivateOrForbiddenError(
                f"Access to {resource_desc} is forbidden. The repository may be private or restricted."
            )

        if response.status_code == 404:
            raise RepoNotFoundError(f"Resource {resource_desc} was not found on GitHub.")

        raise UpstreamGitHubError(
            f"GitHub API returned error {response.status_code} while accessing {resource_desc}."
        )

    async def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository metadata."""
        url = f"{self.API_BASE}/repos/{owner}/{repo}"
        try:
            resp = await self.client.get(url)
            self._handle_response_status(resp, f"repository '{owner}/{repo}'")
            return resp.json()
        except httpx.TimeoutException:
            raise GitHubTimeoutError(f"Timed out fetching repository '{owner}/{repo}'.")
        except httpx.RequestError as e:
            raise UpstreamGitHubError(f"Network error accessing GitHub API: {e.__class__.__name__}")

    async def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch language breakdown in bytes."""
        url = f"{self.API_BASE}/repos/{owner}/{repo}/languages"
        try:
            resp = await self.client.get(url)
            self._handle_response_status(resp, f"languages for '{owner}/{repo}'")
            return resp.json()
        except httpx.TimeoutException:
            raise GitHubTimeoutError(f"Timed out fetching languages for '{owner}/{repo}'.")
        except httpx.RequestError as e:
            raise UpstreamGitHubError(f"Network error accessing GitHub API: {e.__class__.__name__}")

    async def get_readme(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Fetch README metadata and content.
        Returns None if repository does not have a README (404 is normal).
        """
        url = f"{self.API_BASE}/repos/{owner}/{repo}/readme"
        try:
            resp = await self.client.get(url)
            if resp.status_code == 404:
                return None
            self._handle_response_status(resp, f"README for '{owner}/{repo}'")
            return resp.json()
        except httpx.TimeoutException:
            raise GitHubTimeoutError(f"Timed out fetching README for '{owner}/{repo}'.")
        except httpx.RequestError as e:
            raise UpstreamGitHubError(f"Network error accessing GitHub API: {e.__class__.__name__}")

    async def get_tree(self, owner: str, repo: str, branch_or_sha: str) -> Dict[str, Any]:
        """Fetch the full recursive Git tree."""
        url = f"{self.API_BASE}/repos/{owner}/{repo}/git/trees/{branch_or_sha}?recursive=1"
        try:
            resp = await self.client.get(url)
            self._handle_response_status(resp, f"tree for '{owner}/{repo}'")
            return resp.json()
        except httpx.TimeoutException:
            raise GitHubTimeoutError(f"Timed out fetching Git tree for '{owner}/{repo}'.")
        except httpx.RequestError as e:
            raise UpstreamGitHubError(f"Network error accessing GitHub API: {e.__class__.__name__}")

    async def fetch_raw_file(
        self,
        owner: str,
        repo: str,
        branch: str,
        path: str,
        max_bytes: int = 102400
    ) -> Tuple[Optional[str], bool]:
        """
        Fetch a raw source/manifest file via raw.githubusercontent.com.
        Streams content up to max_bytes.
        Returns: (content_str, was_truncated)
        If file exceeds max_bytes, returns (None, True).
        """
        url = f"{self.RAW_BASE}/{owner}/{repo}/{branch}/{path}"
        try:
            # Send Authorization header only if token configured
            async with self.client.stream("GET", url) as resp:
                if resp.status_code == 404:
                    return None, False
                if resp.status_code in (403, 429):
                    self._handle_response_status(resp, f"raw file '{path}'")
                if resp.status_code != 200:
                    return None, False

                content_chunks = []
                total_bytes = 0

                async for chunk in resp.aiter_bytes():
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        # Exceeded limit; abort reading this file
                        return None, True
                    content_chunks.append(chunk)

                raw_bytes = b"".join(content_chunks)
                # Decode as utf-8 with replacement for any non-utf8 characters
                text = raw_bytes.decode("utf-8", errors="replace")
                return text, False
        except httpx.TimeoutException:
            raise GitHubTimeoutError(f"Timed out fetching raw file '{path}'.")
        except httpx.RequestError as e:
            raise UpstreamGitHubError(f"Network error fetching raw file '{path}': {e.__class__.__name__}")
