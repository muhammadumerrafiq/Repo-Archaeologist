import logging
import re
from typing import Optional
from .config import settings

class TokenRedactingFilter(logging.Filter):
    """
    Log filter that intercepts and redacts GitHub personal access tokens
    and Authorization headers from log records.
    """

    BEARER_PATTERN = re.compile(r"(Bearer\s+)[a-zA-Z0-9_\-]+", re.IGNORECASE)
    AUTH_HEADER_PATTERN = re.compile(r"(Authorization['\":\s]+)[^\s,}\"']+", re.IGNORECASE)
    TOKEN_PREFIX_PATTERN = re.compile(r"(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})")

    def __init__(self, token: Optional[str] = None):
        super().__init__()
        self.token = token or settings.GITHUB_TOKEN

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact_string(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact_value(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact_value(v) for v in record.args)
        return True

    def redact_string(self, text: str) -> str:
        if not text:
            return text
        if self.token and self.token in text:
            text = text.replace(self.token, "[REDACTED_TOKEN]")
        text = self.BEARER_PATTERN.sub(r"\1[REDACTED]", text)
        text = self.AUTH_HEADER_PATTERN.sub(r"\1[REDACTED]", text)
        text = self.TOKEN_PREFIX_PATTERN.sub("[REDACTED_TOKEN]", text)
        return text

    def redact_value(self, val):
        if isinstance(val, str):
            return self.redact_string(val)
        return val

def setup_logging():
    logger = logging.getLogger("repo_archaeologist")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    handler.addFilter(TokenRedactingFilter())
    logger.handlers = [handler]
    return logger
