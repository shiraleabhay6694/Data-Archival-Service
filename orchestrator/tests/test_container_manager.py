import pytest
from unittest.mock import MagicMock, patch


class TestContainerManager:
    @pytest.fixture
    def spawn_params(self):
        return {
            "config_id": 1,
            "job_type": "archival",
            "job_execution_id": 100,
            "primary_db_config": {"host": "p-db", "port": 3306, "name": "prod", "user": "root", "password": "x"},
            "archival_db_config": {"host": "a-db", "port": 3306, "name": "arch", "user": "root", "password": "x"},
            "table_config": {"table_name": "orders", "date_column": "created_at", "archival_days": 180, "deletion_days": 730}
        }
    
    def test_spawn_worker_returns_container_id(self, spawn_params):
        from orchestrator.scheduler.container_manager import ContainerManager
        mgr = ContainerManager()
        
        mock_client = MagicMock()
        container = MagicMock()
        container.id = "container_123"
        mock_client.containers.run.return_value = container
        mgr.client = mock_client
        
        with patch('orchestrator.scheduler.container_manager.settings') as mock_s:
            mock_s.worker_image = "img"
            mock_s.docker_network = "net"
            mock_s.orchestrator_db_host = "h"
            mock_s.orchestrator_db_port = 3306
            mock_s.orchestrator_db_name = "db"
            mock_s.orchestrator_db_user = "u"
            mock_s.orchestrator_db_password = "p"
            result = mgr.spawn_worker(**spawn_params)
        
        assert result == "container_123"
