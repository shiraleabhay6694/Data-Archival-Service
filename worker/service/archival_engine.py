from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ArchivalEngine:
    
    def __init__(self, config):
        self.config = config
        self.primary_engine = None
        self.archival_engine = None
        self.stats = {'records_processed': 0, 'records_archived': 0, 'errors': 0}
    
    def connect(self):
        try:
            self.primary_engine = create_engine(self.config.primary_db_url, pool_pre_ping=True)
            self.archival_engine = create_engine(self.config.archival_db_url, pool_pre_ping=True)
            
            with self.primary_engine.connect() as c:
                c.execute(text("SELECT 1"))
            with self.archival_engine.connect() as c:
                c.execute(text("SELECT 1"))
            
            logger.info("DB connections established")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def execute_archival(self):
        try:
            logger.info(f"Archiving table: {self.config.table_name}")
            
            if not self._ensure_archive_table():
                return self.stats
            
            cutoff = datetime.now() - timedelta(days=self.config.archival_days)
            logger.info(f"Cutoff date: {cutoff}")
            
            total = 0
            batch = 0
            while True:
                batch += 1
                count = self._archive_batch(cutoff, batch)
                if count == 0:
                    break
                total += count
                logger.info(f"Batch {batch}: {count} records (total: {total})")
            
            self.stats['records_archived'] = total
            return self.stats
            
        except Exception as e:
            logger.error(f"Archival error: {e}")
            self.stats['errors'] += 1
            raise
        finally:
            self._close()
    
    def _ensure_archive_table(self):
        archive_table = f"archive_{self.config.table_name}"
        
        try:
            inspector = inspect(self.archival_engine)
            if archive_table in inspector.get_table_names():
                return True
            
            logger.info(f"Creating {archive_table}")
            
            with self.primary_engine.connect() as conn:
                result = conn.execute(text(f"SHOW CREATE TABLE `{self.config.table_name}`"))
                create_stmt = result.fetchone()[1]
                create_stmt = create_stmt.replace(
                    f"CREATE TABLE `{self.config.table_name}`",
                    f"CREATE TABLE `{archive_table}`"
                )
            
            with self.archival_engine.connect() as conn:
                conn.execute(text(create_stmt))
                conn.commit()
                
                try:
                    conn.execute(text(f"""
                        ALTER TABLE `{archive_table}`
                        ADD COLUMN IF NOT EXISTS `archived_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ADD COLUMN IF NOT EXISTS `archived_by` VARCHAR(50) DEFAULT 'DAS'
                    """))
                    conn.commit()
                except Exception:
                    pass
            
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to create archive table: {e}")
            return False
    
    def _archive_batch(self, cutoff, batch_num):
        archive_table = f"archive_{self.config.table_name}"
        
        try:
            primary_conn = self.primary_engine.connect()
            archive_conn = self.archival_engine.connect()
            
            primary_tx = primary_conn.begin()
            archive_tx = archive_conn.begin()
            
            try:
                result = primary_conn.execute(text(f"""
                    SELECT * FROM `{self.config.table_name}`
                    WHERE `{self.config.date_column}` < :cutoff
                    LIMIT :batch_size
                """), {'cutoff': cutoff, 'batch_size': self.config.batch_size})
                
                records = result.fetchall()
                if not records:
                    primary_tx.rollback()
                    archive_tx.rollback()
                    return 0
                
                columns = list(result.keys())
                col_names = ', '.join([f"`{c}`" for c in columns])
                placeholders = ', '.join([f":{c}" for c in columns])
                
                insert_q = text(f"INSERT INTO `{archive_table}` ({col_names}) VALUES ({placeholders})")
                
                pk_values = []
                for rec in records:
                    rec_dict = dict(zip(columns, rec))
                    archive_conn.execute(insert_q, rec_dict)
                    if 'id' in rec_dict:
                        pk_values.append(rec_dict['id'])
                
                if pk_values:
                    pk_list = ', '.join(str(pk) for pk in pk_values)
                    primary_conn.execute(text(f"DELETE FROM `{self.config.table_name}` WHERE id IN ({pk_list})"))
                
                archive_tx.commit()
                primary_tx.commit()
                
                self.stats['records_processed'] += len(records)
                return len(records)
                
            except Exception as e:
                primary_tx.rollback()
                archive_tx.rollback()
                raise
            finally:
                primary_conn.close()
                archive_conn.close()
                
        except Exception as e:
            logger.error(f"Batch {batch_num} error: {e}")
            self.stats['errors'] += 1
            return 0
    
    def _close(self):
        if self.primary_engine:
            self.primary_engine.dispose()
        if self.archival_engine:
            self.archival_engine.dispose()
