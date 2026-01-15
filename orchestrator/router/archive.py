from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from orchestrator.repository.database import get_db
from orchestrator.service.archive_service import archive_service
from orchestrator.service.auth_service import auth_service
from orchestrator.security.auth import get_current_user
from .schema.archive import ArchivalDataResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/archive", tags=["Archive"])


@router.get("/{table_name}", response_model=ArchivalDataResponse)
async def get_archived_data(
    table_name: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    roles = current_user.get("roles", [])
    if not auth_service.check_role_permission(roles, table_name):
        raise HTTPException(status_code=403, detail=f"Access denied for table '{table_name}'")
    
    try:
        result = archive_service.get_archived_data(
            db=db,
            table_name=table_name,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        return ArchivalDataResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching archived data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/{job_type}")
async def trigger_job(job_type: str, current_user: dict = Depends(get_current_user)):
    if not auth_service.is_admin(current_user.get("roles", [])):
        raise HTTPException(status_code=403, detail="Admin required")
    
    try:
        archive_service.trigger_job(job_type)
        return {"message": f"{job_type} triggered", "triggered_by": current_user.get("sub")}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
