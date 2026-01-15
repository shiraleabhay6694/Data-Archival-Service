from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ArchivalConfig(Base):
    __tablename__ = "archival_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Primary Database
    primary_db_host = Column(String(255), nullable=False)
    primary_db_port = Column(Integer, nullable=False, default=3306)
    primary_db_name = Column(String(255), nullable=False)
    primary_db_user_encrypted = Column(Text, nullable=False)
    primary_db_password_encrypted = Column(Text, nullable=False)
    
    # Archival Database
    archival_db_host = Column(String(255), nullable=False)
    archival_db_port = Column(Integer, nullable=False, default=3306)
    archival_db_name = Column(String(255), nullable=False)
    archival_db_user_encrypted = Column(Text, nullable=False)
    archival_db_password_encrypted = Column(Text, nullable=False)
    
    table_name = Column(String(255), nullable=False)
    date_column = Column(String(255), nullable=False, default="created_at")
    
    archival_days = Column(Integer, nullable=False, default=180) 
    deletion_days = Column(Integer, nullable=False, default=730)
    
    enabled = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Index for faster lookups
    __table_args__ = (
        Index('idx_table_enabled', 'table_name', 'enabled'),
    )


class JobExecution(Base):
    __tablename__ = "job_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # 'archival'/'purge'
    
    worker_container_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)  # 'running'/'completed'/'failed'
    
    records_processed = Column(Integer, default=0)
    records_archived = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_config_job_type', 'config_id', 'job_type'),
        Index('idx_status_started', 'status', 'started_at'),
    )


