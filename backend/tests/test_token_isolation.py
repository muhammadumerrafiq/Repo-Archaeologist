import io
import logging
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.logging_config import TokenRedactingFilter

class TestTokenIsolation:
    """Security tests verifying GitHub token is strictly isolated and never leaked."""

    FAKE_TOKEN = "ghp_FakeTokenSecretStringForTesting12345"

    @pytest.mark.asyncio
    async def test_health_endpoint_does_not_reveal_token(self, monkeypatch):
        monkeypatch.setattr(settings, "GITHUB_TOKEN", self.FAKE_TOKEN)
        assert settings.is_token_configured is True

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()

            # Exact allowed fields only
            assert data == {"status": "ok", "github_token_configured": True}

            # Verify token or substring is not present anywhere in raw response body or headers
            raw_body = resp.text
            assert self.FAKE_TOKEN not in raw_body
            assert "FakeTokenSecret" not in raw_body
            for header_name, header_val in resp.headers.items():
                assert self.FAKE_TOKEN not in header_val

    @pytest.mark.asyncio
    async def test_health_endpoint_when_no_token(self, monkeypatch):
        monkeypatch.setattr(settings, "GITHUB_TOKEN", None)
        assert settings.is_token_configured is False

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data == {"status": "ok", "github_token_configured": False}

    def test_log_redaction_filter(self):
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        redactor = TokenRedactingFilter(token=self.FAKE_TOKEN)
        handler.addFilter(redactor)

        logger = logging.getLogger("test_redactor")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        logger.info(f"Connecting with token {self.FAKE_TOKEN} now.")
        logger.info(f"Header: Authorization: Bearer {self.FAKE_TOKEN}")
        logger.info("Normal message without sensitive data.")

        output = log_stream.getvalue()
        assert self.FAKE_TOKEN not in output
        assert "[REDACTED_TOKEN]" in output or "[REDACTED]" in output
        assert "Normal message without sensitive data." in output
