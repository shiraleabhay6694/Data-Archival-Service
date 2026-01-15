import pytest
from unittest.mock import patch


class TestArchiveAPI:
    def test_requires_auth(self, test_client):
        assert test_client.get("/api/v1/archive/orders").status_code == 403
    
    def test_requires_table_role(self, test_client, user_auth_headers):
        resp = test_client.get("/api/v1/archive/customers", headers=user_auth_headers)
        assert resp.status_code == 403
    
    def test_404_for_missing_config(self, test_client, auth_headers):
        resp = test_client.get("/api/v1/archive/nonexistent", headers=auth_headers)
        assert resp.status_code == 404
    
    def test_job_history_returns_list(self, test_client, auth_headers):
        resp = test_client.get("/api/v1/archive/jobs/history", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    
    def test_trigger_requires_admin(self, test_client, user_auth_headers):
        assert test_client.post("/api/v1/archive/trigger/archival", headers=user_auth_headers).status_code == 403
    
    def test_trigger_archival(self, test_client, auth_headers):
        with patch('orchestrator.router.archive.scheduler_service') as svc:
            resp = test_client.post("/api/v1/archive/trigger/archival", headers=auth_headers)
            assert resp.status_code == 200
            svc.trigger_archival_now.assert_called_once()
    
    def test_trigger_purge(self, test_client, auth_headers):
        with patch('orchestrator.router.archive.scheduler_service') as svc:
            resp = test_client.post("/api/v1/archive/trigger/purge", headers=auth_headers)
            assert resp.status_code == 200
            svc.trigger_purge_now.assert_called_once()
