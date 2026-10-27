import logging
from fastapi import APIRouter, HTTPException, status
from ..config import settings
from ..schemas.contract import HealthResponse, AnalyzeRequest, ErrorResponse, ErrorDetail

router = APIRouter(prefix="/api")
logger = logging.getLogger("repo_archaeologist")

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check and configuration status"
)
async def health_check():
    """
    Returns API health status and whether a GitHub token is configured.
    Never exposes the token, its prefix, or its length.
    """
    logger.info("Health check endpoint accessed.")
    return HealthResponse(
        status="ok",
        github_token_configured=settings.is_token_configured
    )
