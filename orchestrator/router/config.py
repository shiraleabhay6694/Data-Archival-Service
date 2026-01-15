from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from orchestrator.repository.database import get_db
from orchestrator.service.config_service import config_service
from orchestrator.security.auth import get_current_user, require_admin
from .schema.config import ArchivalConfigCreate, ArchivalConfigUpdate, ArchivalConfigResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])


@router.get("/archival", response_model=List[ArchivalConfigResponse])
async def list_configs(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return config_service.get_all_configs(db)


@router.get("/archival/{config_id}", response_model=ArchivalConfigResponse)
async def get_config(config_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    config = config_service.get_config_by_id(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Config {config_id} not found")
    return config


@router.post("/archival", response_model=ArchivalConfigResponse, status_code=201)
async def create_config(
    config: ArchivalConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    if config_service.check_duplicate_config(
        db, config.table_name, config.primary_db_host, config.primary_db_name
    ):
        raise HTTPException(status_code=409, detail=f"Config exists for '{config.table_name}'")
    
    db_config = config_service.create_config(
        db=db,
        primary_db_host=config.primary_db_host,
        primary_db_port=config.primary_db_port,
        primary_db_name=config.primary_db_name,
        primary_db_user=config.primary_db_user,
        primary_db_password=config.primary_db_password,
        archival_db_host=config.archival_db_host,
        archival_db_port=config.archival_db_port,
        archival_db_name=config.archival_db_name,
        archival_db_user=config.archival_db_user,
        archival_db_password=config.archival_db_password,
        table_name=config.table_name,
        date_column=config.date_column,
        archival_days=config.archival_days,
        deletion_days=config.deletion_days,
        enabled=config.enabled
    )
    
    logger.info(f"Created config for {config.table_name}")
    return db_config


@router.put("/archival/{config_id}", response_model=ArchivalConfigResponse)
async def update_config(
    config_id: int,
    config: ArchivalConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    db_config = config_service.update_config(
        db, config_id, **config.model_dump(exclude_unset=True)
    )
    if not db_config:
        raise HTTPException(status_code=404, detail=f"Config {config_id} not found")
    return db_config


@router.delete("/archival/{config_id}", status_code=204)
async def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    if not config_service.delete_config(db, config_id):
        raise HTTPException(status_code=404, detail=f"Config {config_id} not found")
