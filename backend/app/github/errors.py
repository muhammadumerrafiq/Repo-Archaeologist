from typing import Optional
from ..schemas.contract import ErrorCode

class GitHubError(Exception):
    """Base exception for all GitHub-related errors."""
    code: ErrorCode = "UPSTREAM_ERROR"

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after

class InvalidRepoUrlError(GitHubError):
    code: ErrorCode = "INVALID_URL"

class UnsupportedHostError(GitHubError):
    code: ErrorCode = "UNSUPPORTED_HOST"

class RepoNotFoundError(GitHubError):
    code: ErrorCode = "NOT_FOUND"

class RepoPrivateOrForbiddenError(GitHubError):
    code: ErrorCode = "PRIVATE_OR_FORBIDDEN"

class RateLimitExceededError(GitHubError):
    code: ErrorCode = "RATE_LIMITED"

class UpstreamGitHubError(GitHubError):
    code: ErrorCode = "UPSTREAM_ERROR"

class GitHubTimeoutError(GitHubError):
    code: ErrorCode = "TIMEOUT"
