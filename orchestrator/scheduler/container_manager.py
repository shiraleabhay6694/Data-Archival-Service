import docker
from docker.errors import DockerException, APIError
from datetime import datetime
import logging
from orchestrator.env.config import settings

logger = logging.getLogger(__name__)


class ContainerManager:
    def __init__(self):
        self.client = None
        self._init_docker()
    
    def _init_docker(self):
        try:
            self.client = docker.DockerClient(base_url=f'unix://{settings.docker_socket}')
            self.client.ping()
            logger.info("Docker client connected")
        except DockerException as e:
            logger.warning(f"Docker unavailable: {e}")
            self.client = None
    
    def spawn_worker(self, config_id, job_type, job_execution_id, primary_db_config, archival_db_config, table_config):
        if not self.client:
            logger.error("Docker not available")
            return None
        
        try:
            env = {
                'CONFIG_ID': str(config_id),
                'JOB_TYPE': job_type,
                'JOB_EXECUTION_ID': str(job_execution_id),
                'PRIMARY_DB_HOST': primary_db_config['host'],
                'PRIMARY_DB_PORT': str(primary_db_config['port']),
                'PRIMARY_DB_NAME': primary_db_config['name'],
                'PRIMARY_DB_USER': primary_db_config['user'],
                'PRIMARY_DB_PASSWORD': primary_db_config['password'],
                'ARCHIVAL_DB_HOST': archival_db_config['host'],
                'ARCHIVAL_DB_PORT': str(archival_db_config['port']),
                'ARCHIVAL_DB_NAME': archival_db_config['name'],
                'ARCHIVAL_DB_USER': archival_db_config['user'],
                'ARCHIVAL_DB_PASSWORD': archival_db_config['password'],
                'TABLE_NAME': table_config['table_name'],
                'DATE_COLUMN': table_config['date_column'],
                'ARCHIVAL_DAYS': str(table_config['archival_days']),
                'DELETION_DAYS': str(table_config['deletion_days']),
                'ORCHESTRATOR_DB_HOST': settings.orchestrator_db_host,
                'ORCHESTRATOR_DB_PORT': str(settings.orchestrator_db_port),
                'ORCHESTRATOR_DB_NAME': settings.orchestrator_db_name,
                'ORCHESTRATOR_DB_USER': settings.orchestrator_db_user,
                'ORCHESTRATOR_DB_PASSWORD': settings.orchestrator_db_password,
            }
            
            name = f"das-worker-{config_id}-{job_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            container = self.client.containers.run(
                image=settings.worker_image,
                name=name,
                environment=env,
                network=settings.docker_network,
                detach=True,
                remove=True,
                labels={
                    'das.service': 'worker',
                    'das.config_id': str(config_id),
                    'das.job_type': job_type,
                    'das.job_execution_id': str(job_execution_id)
                }
            )
            
            logger.info(f"Spawned worker: {container.id[:12]}")
            return container.id
            
        except (APIError, Exception) as e:
            logger.error(f"Failed to spawn worker: {e}")
            return None


container_manager = ContainerManager()
