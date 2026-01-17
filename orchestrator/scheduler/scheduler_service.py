from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from orchestrator.env.config import settings
from orchestrator.repository.database import SessionLocal
from orchestrator.model.models import ArchivalConfig, JobExecution
from orchestrator.security.encryption_service import encryption_service
from .container_manager import container_manager

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._job_running = {'archival': False, 'purge': False}
    
    def start(self):
        self.scheduler.add_job(
            func=self._run_archival_job,
            trigger=CronTrigger.from_crontab(settings.archival_job_cron),
            id='archival_job',
            name='Data Archival Job',
            replace_existing=True
        )
        self.scheduler.add_job(
            func=self._run_purge_job,
            trigger=CronTrigger.from_crontab(settings.purge_job_cron),
            id='purge_job',
            name='Data Purge Job',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"Scheduler jobs started - archival: {settings.archival_job_cron}, purge: {settings.purge_job_cron}")
    
    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def _run_archival_job(self):
        if self._job_running['archival']:
            logger.warning("Archival already running, skipping")
            return
        
        try:
            self._job_running['archival'] = True
            logger.info("Starting archival job")
            
            db = SessionLocal()
            try:
                configs = db.query(ArchivalConfig).filter(ArchivalConfig.enabled == True).all()
                logger.info(f"Found {len(configs)} configs")
                
                for cfg in configs:
                    self._spawn_archival_worker(db, cfg)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Archival job error: {e}")
        finally:
            self._job_running['archival'] = False
    
    def _run_purge_job(self):
        if self._job_running['purge']:
            logger.warning("Purge already running, skipping")
            return
        
        try:
            self._job_running['purge'] = True
            logger.info("Starting purge job")
            
            db = SessionLocal()
            try:
                configs = db.query(ArchivalConfig).filter(ArchivalConfig.enabled == True).all()
                logger.info(f"Found {len(configs)} configs")
                
                for cfg in configs:
                    self._spawn_purge_worker(db, cfg)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Purge job error: {e}")
        finally:
            self._job_running['purge'] = False
    
    def _spawn_archival_worker(self, db: Session, cfg: ArchivalConfig):
        try:
            primary_db = {
                'host': cfg.primary_db_host,
                'port': cfg.primary_db_port,
                'name': cfg.primary_db_name,
                'user': encryption_service.decrypt(cfg.primary_db_user_encrypted),
                'password': encryption_service.decrypt(cfg.primary_db_password_encrypted)
            }
            archive_db = {
                'host': cfg.archival_db_host,
                'port': cfg.archival_db_port,
                'name': cfg.archival_db_name,
                'user': encryption_service.decrypt(cfg.archival_db_user_encrypted),
                'password': encryption_service.decrypt(cfg.archival_db_password_encrypted)
            }
            table_cfg = {
                'table_name': cfg.table_name,
                'date_column': cfg.date_column,
                'archival_days': cfg.archival_days,
                'deletion_days': cfg.deletion_days
            }
            
            job = JobExecution(config_id=cfg.id, job_type='archival', status='running')
            db.add(job)
            db.commit()
            db.refresh(job)
            
            container_id = container_manager.spawn_worker(
                config_id=cfg.id,
                job_type='archival',
                job_execution_id=job.id,
                primary_db_config=primary_db,
                archival_db_config=archive_db,
                table_config=table_cfg
            )
            
            if container_id:
                job.worker_container_id = container_id
                db.commit()
                logger.info(f"Archival worker spawned for {cfg.table_name}")
            else:
                job.status = 'failed'
                job.error_message = 'Failed to spawn worker'
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Error spawning archival worker for config {cfg.id}: {e}")
    
    def _spawn_purge_worker(self, db: Session, cfg: ArchivalConfig):
        try:
            archive_db = {
                'host': cfg.archival_db_host,
                'port': cfg.archival_db_port,
                'name': cfg.archival_db_name,
                'user': encryption_service.decrypt(cfg.archival_db_user_encrypted),
                'password': encryption_service.decrypt(cfg.archival_db_password_encrypted)
            }

            primary_db = {'host': 'n/a', 'port': 0, 'name': 'n/a', 'user': 'n/a', 'password': 'n/a'}
            table_cfg = {
                'table_name': cfg.table_name,
                'date_column': cfg.date_column,
                'archival_days': cfg.archival_days,
                'deletion_days': cfg.deletion_days
            }
            
            job = JobExecution(config_id=cfg.id, job_type='purge', status='running')
            db.add(job)
            db.commit()
            db.refresh(job)
            
            container_id = container_manager.spawn_worker(
                config_id=cfg.id,
                job_type='purge',
                job_execution_id=job.id,
                primary_db_config=primary_db,
                archival_db_config=archive_db,
                table_config=table_cfg
            )
            
            if container_id:
                job.worker_container_id = container_id
                db.commit()
                logger.info(f"Purge worker spawned for {cfg.table_name}")
            else:
                job.status = 'failed'
                job.error_message = 'Failed to spawn worker'
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Error spawning purge worker for config {cfg.id}: {e}")


scheduler_service = SchedulerService()
