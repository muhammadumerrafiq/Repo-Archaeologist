import pytest
from app.github.url_parser import parse_github_url, ParsedRepo
from app.github.errors import InvalidRepoUrlError, UnsupportedHostError

class TestUrlParser:
    """Test suite for strict GitHub repository URL validation."""

    # Valid URLs
    @pytest.mark.parametrize(
        "url,expected_owner,expected_repo",
        [
            ("https://github.com/torvalds/linux", "torvalds", "linux"),
            ("https://github.com/facebook/react/", "facebook", "react"),
            ("https://github.com/tiangolo/fastapi.git", "tiangolo", "fastapi"),
            ("https://github.com/encode/httpx.git/", "encode", "httpx"),
            ("https://github.com/psf/requests", "psf", "requests"),
            ("https://github.com/A-B-C/my-repo_1.0", "A-B-C", "my-repo_1.0"),
            ("https://github.com/owner-1/repo.name", "owner-1", "repo.name"),
            ("  https://github.com/vuejs/core  ", "vuejs", "core"),
        ]
    )
    def test_valid_github_urls(self, url, expected_owner, expected_repo):
        parsed = parse_github_url(url)
        assert isinstance(parsed, ParsedRepo)
        assert parsed.owner == expected_owner
        assert parsed.name == expected_repo
        assert parsed.full_name == f"{expected_owner}/{expected_repo}"
        assert parsed.canonical_url == f"https://github.com/{expected_owner}/{expected_repo}"

    # Malicious / Malformed / Unsupported URLs
    @pytest.mark.parametrize(
        "malformed_url,expected_exception",
        [
            ("http://github.com/owner/repo", InvalidRepoUrlError),  # non-https
            ("git://github.com/owner/repo", InvalidRepoUrlError),   # git scheme
            ("ssh://github.com/owner/repo", InvalidRepoUrlError),   # ssh scheme
            ("ftp://github.com/owner/repo", InvalidRepoUrlError),   # ftp scheme
            ("https://www.github.com/owner/repo", UnsupportedHostError), # www subdomain
            ("https://gist.github.com/owner/123", UnsupportedHostError), # gist host
            ("https://api.github.com/repos/owner/repo", UnsupportedHostError), # api host
            ("https://github.com.evil.com/owner/repo", UnsupportedHostError), # domain spoofing
            ("https://evilgithub.com/owner/repo", UnsupportedHostError), # lookalike domain
            ("https://gitlab.com/owner/repo", UnsupportedHostError), # gitlab
            ("https://bitbucket.org/owner/repo", UnsupportedHostError), # bitbucket
            ("https://192.168.1.1/owner/repo", UnsupportedHostError), # IP host
            ("https://user:pass@github.com/owner/repo", InvalidRepoUrlError), # userinfo
            ("https://github.com:8080/owner/repo", InvalidRepoUrlError), # custom port
            ("https://github.com/owner/repo/tree/main", InvalidRepoUrlError), # extra path segment
            ("https://github.com/owner/repo/blob/main/README.md", InvalidRepoUrlError), # file path
            ("https://github.com/owner/repo?ref=main", InvalidRepoUrlError), # query string
            ("https://github.com/owner/repo#readme", InvalidRepoUrlError), # fragment
            ("https://github.com/owner/%2e%2e/admin", InvalidRepoUrlError), # percent-encoded
            ("https://github.com/owner/%00null", InvalidRepoUrlError), # null byte
            ("https://github.com/owner/", InvalidRepoUrlError), # missing repo
            ("https://github.com//repo", InvalidRepoUrlError), # empty owner
            ("https://github.com/", InvalidRepoUrlError), # empty path
            ("", InvalidRepoUrlError), # empty string
            ("    ", InvalidRepoUrlError), # whitespace
            ("https://github.com/owner/repo\n", InvalidRepoUrlError), # newline control character
            ("https://github.com/" + "a" * 300, InvalidRepoUrlError), # overly long
            ("https://github.com/-invalid-/repo", InvalidRepoUrlError), # invalid owner leading hyphen
            ("https://github.com/owner/..", InvalidRepoUrlError), # traversal in repo
            ("https://github.com/owner/.", InvalidRepoUrlError), # dot repo
        ]
    )
    def test_malformed_and_malicious_urls(self, malformed_url, expected_exception):
        with pytest.raises(expected_exception):
            parse_github_url(malformed_url)
