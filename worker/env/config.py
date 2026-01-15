import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkerConfig:
    config_id: int
    job_type: str
    job_execution_id: Optional[int]

    primary_db_host: str
    primary_db_port: int
    primary_db_name: str
    primary_db_user: str
    primary_db_password: str
    
    archival_db_host: str
    archival_db_port: int
    archival_db_name: str
    archival_db_user: str
    archival_db_password: str
    
    table_name: str
    date_column: str
    archival_days: int
    deletion_days: int
    
    orchestrator_db_host: str
    orchestrator_db_port: int
    orchestrator_db_name: str
    orchestrator_db_user: str
    orchestrator_db_password: str
    
    batch_size: int = 1000
    
    @property
    def primary_db_url(self):
        return (
            f"mysql+pymysql://{self.primary_db_user}:{self.primary_db_password}"
            f"@{self.primary_db_host}:{self.primary_db_port}/{self.primary_db_name}"
        )
    
    @property
    def archival_db_url(self):
        return (
            f"mysql+pymysql://{self.archival_db_user}:{self.archival_db_password}"
            f"@{self.archival_db_host}:{self.archival_db_port}/{self.archival_db_name}"
        )
    
    @property
    def orchestrator_db_url(self):
        return (
            f"mysql+pymysql://{self.orchestrator_db_user}:{self.orchestrator_db_password}"
            f"@{self.orchestrator_db_host}:{self.orchestrator_db_port}/{self.orchestrator_db_name}"
        )
    
    @classmethod
    def from_env(cls):
        return cls(
            config_id=int(os.getenv('CONFIG_ID', '0')),
            job_type=os.getenv('JOB_TYPE', 'archival'),
            job_execution_id=int(os.getenv('JOB_EXECUTION_ID', '0')) or None,
            
            primary_db_host=os.getenv('PRIMARY_DB_HOST', 'localhost'),
            primary_db_port=int(os.getenv('PRIMARY_DB_PORT', '3306')),
            primary_db_name=os.getenv('PRIMARY_DB_NAME', 'primary'),
            primary_db_user=os.getenv('PRIMARY_DB_USER', 'root'),
            primary_db_password=os.getenv('PRIMARY_DB_PASSWORD', ''),
            
            archival_db_host=os.getenv('ARCHIVAL_DB_HOST', 'localhost'),
            archival_db_port=int(os.getenv('ARCHIVAL_DB_PORT', '3306')),
            archival_db_name=os.getenv('ARCHIVAL_DB_NAME', 'archival'),
            archival_db_user=os.getenv('ARCHIVAL_DB_USER', 'root'),
            archival_db_password=os.getenv('ARCHIVAL_DB_PASSWORD', ''),
            
            table_name=os.getenv('TABLE_NAME', ''),
            date_column=os.getenv('DATE_COLUMN', 'created_at'),
            archival_days=int(os.getenv('ARCHIVAL_DAYS', '180')),
            deletion_days=int(os.getenv('DELETION_DAYS', '730')),
            
            orchestrator_db_host=os.getenv('ORCHESTRATOR_DB_HOST', 'localhost'),
            orchestrator_db_port=int(os.getenv('ORCHESTRATOR_DB_PORT', '3306')),
            orchestrator_db_name=os.getenv('ORCHESTRATOR_DB_NAME', 'archival_orchestrator'),
            orchestrator_db_user=os.getenv('ORCHESTRATOR_DB_USER', 'root'),
            orchestrator_db_password=os.getenv('ORCHESTRATOR_DB_PASSWORD', ''),
            
            batch_size=int(os.getenv('BATCH_SIZE', '1000'))
        )


config = WorkerConfig.from_env()
