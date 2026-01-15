import pytest
from unittest.mock import MagicMock, patch


class TestSchedulerService:
    def test_start_adds_jobs(self):
        from orchestrator.scheduler.scheduler_service import SchedulerService
        svc = SchedulerService()
        svc.scheduler = MagicMock()
        
        with patch('orchestrator.scheduler.scheduler_service.settings') as mock_s:
            mock_s.archival_job_cron = "0 2 * * *"
            mock_s.purge_job_cron = "0 3 * * *"
            svc.start()
        
        assert svc.scheduler.add_job.call_count == 2
        svc.scheduler.start.assert_called_once()
    
    def test_stop_shuts_down(self):
        from orchestrator.scheduler.scheduler_service import SchedulerService
        svc = SchedulerService()
        svc.scheduler = MagicMock()
        svc.scheduler.running = True
        svc.stop()
        svc.scheduler.shutdown.assert_called_once()
    
    def test_trigger_archival(self):
        from orchestrator.scheduler.scheduler_service import SchedulerService
        svc = SchedulerService()
        svc._run_archival_job = MagicMock()
        svc.trigger_archival_now()
        svc._run_archival_job.assert_called_once()
    
    def test_trigger_purge(self):
        from orchestrator.scheduler.scheduler_service import SchedulerService
        svc = SchedulerService()
        svc._run_purge_job = MagicMock()
        svc.trigger_purge_now()
        svc._run_purge_job.assert_called_once()
