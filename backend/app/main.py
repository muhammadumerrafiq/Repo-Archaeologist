from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .logging_config import setup_logging
from .api.routes import router
from .github.errors import (
    GitHubError,
    InvalidRepoUrlError,
    UnsupportedHostError,
    RepoNotFoundError,
    RepoPrivateOrForbiddenError,
    RateLimitExceededError,
    UpstreamGitHubError,
    GitHubTimeoutError,
)

logger = setup_logging()

app = FastAPI(
    title="Repo Archaeologist API",
    description="Deterministic visual surveying engine for public GitHub repositories",
    version="1.0.0"
)

# CORS configuration strictly restricted to allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Exception Handlers ensuring standardized ErrorResponse shape
@app.exception_handler(GitHubError)
async def github_error_handler(request: Request, exc: GitHubError):
    status_map = {
        "INVALID_URL": status.HTTP_400_BAD_REQUEST,
        "UNSUPPORTED_HOST": status.HTTP_400_BAD_REQUEST,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "PRIVATE_OR_FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "RATE_LIMITED": status.HTTP_429_TOO_MANY_REQUESTS,
        "TIMEOUT": status.HTTP_504_GATEWAY_TIMEOUT,
        "UPSTREAM_ERROR": status.HTTP_502_BAD_GATEWAY,
    }
    http_status = status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.warning("GitHub error handled [%s]: %s", exc.code, exc.message)
    return JSONResponse(
        status_code=http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retry_after": exc.retry_after
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    error_msg = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.warning("Request validation error: %s", error_msg)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_URL",
                "message": f"Invalid request: {error_msg}",
                "retry_after": None
            }
        }
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "An unexpected internal error occurred.",
                "retry_after": None
            }
        }
    )

app.include_router(router)
