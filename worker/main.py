import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from worker.env.config import config
from worker.service.archival_engine import ArchivalEngine
from worker.service.purge_engine import PurgeEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    start_time = datetime.now()
    
    logger.info(f"Worker starting - job_type={config.job_type}, table={config.table_name}")
    logger.info(f"Config: archival_days={config.archival_days}, deletion_days={config.deletion_days}")
    
    stats = {'records_processed': 0, 'records_archived': 0, 'records_deleted': 0, 'errors': 0}
    
    try:
        if config.job_type == 'archival':
            stats = run_archival()
        elif config.job_type == 'purge':
            stats = run_purge()
        else:
            logger.error(f"Unknown job type: {config.job_type}")
            update_job_status('failed', stats, f"Unknown job type: {config.job_type}")
            sys.exit(1)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Job completed in {duration:.2f}s - {stats}")
        
        update_job_status('completed', stats)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        update_job_status('failed', stats, str(e))
        sys.exit(1)


def run_archival():
    engine = ArchivalEngine(config)
    
    if not engine.connect():
        raise Exception("Database connection failed")
    
    stats = engine.execute_archival()
    logger.info(f"Archival done: processed={stats['records_processed']}, archived={stats['records_archived']}")
    
    if stats['errors'] > 0:
        raise Exception(f"Archival completed with {stats['errors']} errors")
    
    return stats


def run_purge():
    engine = PurgeEngine(config)
    
    if not engine.connect():
        raise Exception("Database connection failed")
    
    stats = engine.execute_purge()
    logger.info(f"Purge done: deleted={stats['records_deleted']}")
    
    if stats['errors'] > 0:
        raise Exception(f"Purge completed with {stats['errors']} errors")
    
    return stats


def update_job_status(status, stats, error_message=None):
    if not config.job_execution_id:
        return
    
    try:
        engine = create_engine(config.orchestrator_db_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE job_executions 
                SET status = :status,
                    records_processed = :records_processed,
                    records_archived = :records_archived,
                    records_deleted = :records_deleted,
                    completed_at = UTC_TIMESTAMP(),
                    error_message = :error_message
                WHERE id = :job_id
            """), {
                'status': status,
                'records_processed': stats.get('records_processed', 0),
                'records_archived': stats.get('records_archived', 0),
                'records_deleted': stats.get('records_deleted', 0),
                'error_message': error_message,
                'job_id': config.job_execution_id
            })
            conn.commit()
            
    except Exception as e:
        logger.error(f"Failed to update job status: {e}")


if __name__ == "__main__":
    main()
