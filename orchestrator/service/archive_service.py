from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from orchestrator.repository.archival_config_repository import archival_config_repository
from orchestrator.security.encryption_service import encryption_service
from orchestrator.scheduler.scheduler_service import scheduler_service
import logging

logger = logging.getLogger(__name__)


class ArchiveService:
    
    def get_archived_data(
        self,
        db: Session,
        table_name: str,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        config = archival_config_repository.get_by_table_name(db, table_name)
        if not config:
            raise ValueError(f"No config for table '{table_name}'")
        
        db_url = (
            f"mysql+pymysql://{encryption_service.decrypt(config.archival_db_user_encrypted)}:"
            f"{encryption_service.decrypt(config.archival_db_password_encrypted)}@"
            f"{config.archival_db_host}:{config.archival_db_port}/{config.archival_db_name}"
        )
        engine = create_engine(db_url, pool_pre_ping=True)
        archive_table = f"archive_{table_name}"
        
        with engine.connect() as conn:
            where_parts = []
            params = {"limit": limit, "offset": offset}
            
            if start_date:
                where_parts.append(f"{config.date_column} >= :start_date")
                params["start_date"] = start_date
            if end_date:
                where_parts.append(f"{config.date_column} <= :end_date")
                params["end_date"] = end_date
            
            where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
            
            total = conn.execute(
                text(f"SELECT COUNT(*) FROM {archive_table} {where}"),
                params
            ).scalar()
            
            result = conn.execute(text(f"""
                SELECT * FROM {archive_table} {where}
                ORDER BY {config.date_column} DESC
                LIMIT :limit OFFSET :offset
            """), params)
            
            columns = result.keys()
            records = []
            for row in result.fetchall():
                rec = dict(zip(columns, row))
                for k, v in rec.items():
                    if hasattr(v, 'isoformat'):
                        rec[k] = v.isoformat()
                records.append(rec)
        
        return {
            "table_name": archive_table,
            "total_records": total,
            "records": records
        }


# Global archive service instance
archive_service = ArchiveService()
