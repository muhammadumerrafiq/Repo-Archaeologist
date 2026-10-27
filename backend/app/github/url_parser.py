import re
from urllib.parse import urlsplit
from typing import Tuple, NamedTuple
from .errors import InvalidRepoUrlError, UnsupportedHostError

class ParsedRepo(NamedTuple):
    owner: str
    name: str
    full_name: str
    canonical_url: str

OWNER_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$")
REPO_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{1,100}$")

def parse_github_url(raw_url: str) -> ParsedRepo:
    """
    Strictly validates and parses a GitHub repository URL.
    Only allows: https://github.com/owner/repo[.git][/]
    Rejects SSRF attempts, non-HTTPS schemes, other hosts, userinfo, ports, subpaths, etc.
    """
    if not isinstance(raw_url, str):
        raise InvalidRepoUrlError("URL must be a string.")

    # Reject control characters anywhere in the raw input (including newline, carriage return, tabs)
    if any(ord(c) < 32 or ord(c) == 127 for c in raw_url):
        raise InvalidRepoUrlError("Repository URL contains illegal control characters.")

    url = raw_url.strip()
    if not url:
        raise InvalidRepoUrlError("Repository URL cannot be empty.")

    if len(url) > 256:
        raise InvalidRepoUrlError("Repository URL exceeds maximum allowed length of 256 characters.")

    # Reject internal whitespace
    if any(c.isspace() for c in url):
        raise InvalidRepoUrlError("Repository URL contains illegal whitespace.")

    # Reject percent-encoding tricks
    if "%" in url:
        raise InvalidRepoUrlError("Percent-encoded characters are not permitted in the repository URL.")

    # Parse URL
    try:
        parsed = urlsplit(url)
    except Exception as e:
        raise InvalidRepoUrlError(f"Malformed URL: {e}")

    # Scheme validation: strictly https
    if parsed.scheme != "https":
        if parsed.scheme in ("http", "git", "ssh", "ftp"):
            raise InvalidRepoUrlError(f"Scheme '{parsed.scheme}' is not supported. Please use 'https://'.")
        raise InvalidRepoUrlError("Invalid URL scheme. Only 'https://' is permitted.")

    # Userinfo validation
    if parsed.username or parsed.password or "@" in (parsed.netloc or ""):
        raise InvalidRepoUrlError("Userinfo credentials are not permitted in the repository URL.")

    # Port validation
    if parsed.port is not None or ":" in (parsed.netloc or ""):
        raise InvalidRepoUrlError("Custom ports are not permitted in the repository URL.")

    # Host validation: strictly github.com
    host = (parsed.hostname or "").lower()
    if not host:
        raise InvalidRepoUrlError("Missing hostname in repository URL.")

    if host != "github.com":
        if host in ("gitlab.com", "bitbucket.org", "sourceforge.net", "codeberg.org"):
            raise UnsupportedHostError(f"Host '{host}' is not supported. Repo Archaeologist only surveys GitHub repositories.")
        raise UnsupportedHostError(f"Host '{host}' is invalid or unsupported. Only 'github.com' is allowed.")

    # Query and fragment validation
    if parsed.query or parsed.fragment:
        raise InvalidRepoUrlError("Query parameters and URL fragments are not permitted.")

    # Path validation
    path = parsed.path.strip("/")
    if not path:
        raise InvalidRepoUrlError("Missing repository path. Expected 'owner/repo'.")

    segments = path.split("/")
    if len(segments) != 2:
        if len(segments) > 2:
            raise InvalidRepoUrlError(
                f"Path contains extra segments: '{path}'. Please provide the root repository URL "
                "(e.g. https://github.com/owner/repo) without branch, commit, or folder subpaths."
            )
        raise InvalidRepoUrlError(f"Incomplete repository path: '{path}'. Expected 'owner/repo'.")

    owner, repo_segment = segments

    # Strip optional trailing .git
    if repo_segment.endswith(".git"):
        repo_name = repo_segment[:-4]
    else:
        repo_name = repo_segment

    # Validate owner name
    if not OWNER_REGEX.match(owner):
        raise InvalidRepoUrlError(f"Invalid GitHub owner name: '{owner}'.")

    # Validate repo name
    if not REPO_REGEX.match(repo_name) or repo_name in (".", ".."):
        raise InvalidRepoUrlError(f"Invalid GitHub repository name: '{repo_name}'.")

    full_name = f"{owner}/{repo_name}"
    canonical_url = f"https://github.com/{full_name}"

    return ParsedRepo(
        owner=owner,
        name=repo_name,
        full_name=full_name,
        canonical_url=canonical_url
    )
