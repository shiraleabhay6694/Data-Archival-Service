from fastapi import APIRouter, HTTPException
from .schema.auth import CreateTokenRequest, TokenResponse
from orchestrator.service.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
def create_token(request: CreateTokenRequest):
    try:
        token_data = auth_service.create_token(
            username=request.username,
            roles=request.roles
        )
        return TokenResponse(**token_data)
    except Exception as e:
        logger.error(f"Token error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
