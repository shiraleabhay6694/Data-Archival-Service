from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PurgeEngine:
    
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.stats = {'records_processed': 0, 'records_deleted': 0, 'errors': 0}
    
    def connect(self):
        try:
            self.engine = create_engine(self.config.archival_db_url, pool_pre_ping=True)
            with self.engine.connect() as c:
                c.execute(text("SELECT 1"))
            logger.info("Connected to archive DB")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def execute_purge(self):
        try:
            archive_table = f"archive_{self.config.table_name}"
            cutoff = datetime.now() - timedelta(days=self.config.deletion_days)
            
            logger.info(f"Purging {archive_table}, cutoff: {cutoff}")
            
            if not self._table_exists(archive_table):
                logger.warning(f"Table {archive_table} doesn't exist")
                return self.stats
            
            initial = self._count_records(archive_table, cutoff)
            logger.info(f"Records to purge: {initial}")
            
            total = 0
            batch = 0
            while True:
                batch += 1
                count = self._purge_batch(archive_table, cutoff)
                if count == 0:
                    break
                total += count
                logger.info(f"Batch {batch}: deleted {count} (total: {total})")
            
            self.stats['records_deleted'] = total
            self.stats['records_processed'] = total
            return self.stats
            
        except Exception as e:
            logger.error(f"Purge error: {e}")
            self.stats['errors'] += 1
            raise
        finally:
            if self.engine:
                self.engine.dispose()
    
    def _table_exists(self, table_name):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = :db AND table_name = :table
                """), {'db': self.config.archival_db_name, 'table': table_name})
                return result.scalar() > 0
        except Exception:
            return False
    
    def _count_records(self, table_name, cutoff):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) FROM `{table_name}`
                    WHERE `{self.config.date_column}` < :cutoff
                """), {'cutoff': cutoff})
                return result.scalar()
        except Exception:
            return 0
    
    def _purge_batch(self, table_name, cutoff):
        try:
            with self.engine.connect() as conn:
                tx = conn.begin()
                try:
                    result = conn.execute(text(f"""
                        DELETE FROM `{table_name}`
                        WHERE `{self.config.date_column}` < :cutoff
                        LIMIT :batch_size
                    """), {'cutoff': cutoff, 'batch_size': self.config.batch_size})
                    tx.commit()
                    return result.rowcount
                except Exception:
                    tx.rollback()
                    raise
        except Exception as e:
            logger.error(f"Purge batch error: {e}")
            self.stats['errors'] += 1
            return 0
