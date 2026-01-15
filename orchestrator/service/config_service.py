from typing import List, Optional
from sqlalchemy.orm import Session
from orchestrator.model.models import ArchivalConfig
from orchestrator.repository.archival_config_repository import archival_config_repository
from orchestrator.security.encryption_service import encryption_service
import logging

logger = logging.getLogger(__name__)


class ConfigService:
    
    def get_all_configs(self, db: Session) -> List[ArchivalConfig]:
        return archival_config_repository.get_all(db)
    
    def get_config_by_id(self, db: Session, config_id: int) -> Optional[ArchivalConfig]:
        return archival_config_repository.get_by_id(db, config_id)
    
    def check_duplicate_config(
        self,
        db: Session,
        table_name: str,
        primary_db_host: str,
        primary_db_name: str
    ) -> bool:
        return archival_config_repository.check_exists(
            db, table_name, primary_db_host, primary_db_name
        )
    
    def create_config(
        self,
        db: Session,
        primary_db_host: str,
        primary_db_port: int,
        primary_db_name: str,
        primary_db_user: str,
        primary_db_password: str,
        archival_db_host: str,
        archival_db_port: int,
        archival_db_name: str,
        archival_db_user: str,
        archival_db_password: str,
        table_name: str,
        date_column: str = "created_at",
        archival_days: int = 180,
        deletion_days: int = 730,
        enabled: bool = True
    ) -> ArchivalConfig:
        
        config = ArchivalConfig(
            primary_db_host=primary_db_host,
            primary_db_port=primary_db_port,
            primary_db_name=primary_db_name,
            primary_db_user_encrypted=encryption_service.encrypt(primary_db_user),
            primary_db_password_encrypted=encryption_service.encrypt(primary_db_password),
            archival_db_host=archival_db_host,
            archival_db_port=archival_db_port,
            archival_db_name=archival_db_name,
            archival_db_user_encrypted=encryption_service.encrypt(archival_db_user),
            archival_db_password_encrypted=encryption_service.encrypt(archival_db_password),
            table_name=table_name,
            date_column=date_column,
            archival_days=archival_days,
            deletion_days=deletion_days,
            enabled=enabled
        )
        
        created_config = archival_config_repository.create(db, config)
        logger.info(f"Created archival config for table: {table_name}")
        return created_config
    
    def update_config(
        self,
        db: Session,
        config_id: int,
        **kwargs
    ) -> Optional[ArchivalConfig]:
        config = archival_config_repository.get_by_id(db, config_id)
        
        if not config:
            return None
        
        updated_config = archival_config_repository.update(db, config, kwargs)
        logger.info(f"Updated archival config {config_id}")
        return updated_config
    
    def delete_config(self, db: Session, config_id: int) -> bool:
        config = archival_config_repository.get_by_id(db, config_id)
        
        if not config:
            return False
        
        archival_config_repository.delete(db, config)
        logger.info(f"Deleted archival config {config_id}")
        return True


# Global config service instance
config_service = ConfigService()
