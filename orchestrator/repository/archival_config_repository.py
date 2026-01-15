from typing import List, Optional
from sqlalchemy.orm import Session
from orchestrator.model.models import ArchivalConfig


class ArchivalConfigRepository:
    
    def get_all(self, db: Session) -> List[ArchivalConfig]:
        return db.query(ArchivalConfig).all()
    
    def get_by_id(self, db: Session, config_id: int) -> Optional[ArchivalConfig]:
        return db.query(ArchivalConfig).filter(
            ArchivalConfig.id == config_id
        ).first()
    
    def get_by_table_name(self, db: Session, table_name: str) -> Optional[ArchivalConfig]:
        return db.query(ArchivalConfig).filter(
            ArchivalConfig.table_name == table_name
        ).first()
    
    def check_exists(
        self,
        db: Session,
        table_name: str,
        primary_db_host: str,
        primary_db_name: str
    ) -> bool:
        existing = db.query(ArchivalConfig).filter(
            ArchivalConfig.table_name == table_name,
            ArchivalConfig.primary_db_host == primary_db_host,
            ArchivalConfig.primary_db_name == primary_db_name
        ).first()
        return existing is not None
    
    def create(self, db: Session, config: ArchivalConfig) -> ArchivalConfig:
        db.add(config)
        db.commit()
        db.refresh(config)
        return config
    
    def update(self, db: Session, config: ArchivalConfig, updates: dict) -> ArchivalConfig:
        for field, value in updates.items():
            if hasattr(config, field) and value is not None:
                setattr(config, field, value)
        db.commit()
        db.refresh(config)
        return config
    
    def delete(self, db: Session, config: ArchivalConfig) -> None:
        db.delete(config)
        db.commit()


archival_config_repository = ArchivalConfigRepository()
