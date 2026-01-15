from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ArchivalConfigBase(BaseModel):
    primary_db_host: str
    primary_db_port: int = Field(default=3306)
    primary_db_name: str
    primary_db_user: str
    primary_db_password: str
    
    archival_db_host: str
    archival_db_port: int = Field(default=3306)
    archival_db_name: str
    archival_db_user: str
    archival_db_password: str
    
    table_name: str
    date_column: str = "created_at"
    archival_days: int = Field(default=180, ge=1)
    deletion_days: int = Field(default=730, ge=1)
    enabled: bool = True
    
    @field_validator('table_name')
    @classmethod
    def validate_table_name(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Invalid table name')
        return v
    
    @field_validator('deletion_days')
    @classmethod
    def validate_deletion_days(cls, v, info):
        if 'archival_days' in info.data and v <= info.data['archival_days']:
            raise ValueError('deletion_days must be > archival_days')
        return v


class ArchivalConfigCreate(ArchivalConfigBase):
    pass


class ArchivalConfigUpdate(BaseModel):
    archival_days: Optional[int] = Field(None, ge=1)
    deletion_days: Optional[int] = Field(None, ge=1)
    enabled: Optional[bool] = None
    date_column: Optional[str] = None


class ArchivalConfigResponse(BaseModel):
    id: int
    primary_db_host: str
    primary_db_port: int
    primary_db_name: str
    archival_db_host: str
    archival_db_port: int
    archival_db_name: str
    table_name: str
    date_column: str
    archival_days: int
    deletion_days: int
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
