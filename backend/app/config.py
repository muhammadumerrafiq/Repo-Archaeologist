from typing import List, Optional
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub Classic Personal Access Token")
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        description="Allowed CORS origins (comma-separated, no wildcards allowed)"
    )
    CACHE_TTL_SECONDS: int = Field(default=600, description="In-memory cache TTL in seconds")
    MAX_FILES_TO_FETCH: int = Field(default=40, description="Max raw files to fetch per analysis")
    MAX_BYTES_PER_FILE: int = Field(default=102400, description="Max bytes per raw file (100 KB)")
    MAX_TOTAL_BYTES: int = Field(default=2097152, description="Max cumulative bytes fetched (2 MB)")
    REQUEST_TIMEOUT_SECONDS: float = Field(default=25.0, description="GitHub API request timeout")

    @property
    def allowed_origins_list(self) -> List[str]:
        origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        for o in origins:
            if o == "*":
                raise ValueError("CORS wildcard '*' is strictly prohibited by security rules.")
        return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def is_token_configured(self) -> bool:
        return bool(self.GITHUB_TOKEN and self.GITHUB_TOKEN.strip())

settings = Settings()
