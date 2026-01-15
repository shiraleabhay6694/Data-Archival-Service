from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


class JobStatusResponse(BaseModel):
    archival_jobs: dict
    purge_jobs: dict
    next_archival_run: Optional[str] = None
    next_purge_run: Optional[str] = None
