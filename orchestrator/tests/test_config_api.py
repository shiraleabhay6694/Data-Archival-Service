import pytest


class TestConfigAPI:
    def test_list_configs(self, test_client, auth_headers):
        resp = test_client.get("/api/v1/config/archival", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
    
    def test_create_config(self, test_client, auth_headers, sample_archival_config):
        resp = test_client.post("/api/v1/config/archival", headers=auth_headers, json=sample_archival_config)
        assert resp.status_code == 201
        assert resp.json()["table_name"] == sample_archival_config["table_name"]
    
    def test_get_config(self, test_client, auth_headers, sample_archival_config_db):
        cid = sample_archival_config_db.id
        resp = test_client.get(f"/api/v1/config/archival/{cid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["table_name"] == "orders"
    
    def test_update_config(self, test_client, auth_headers, sample_archival_config_db):
        cid = sample_archival_config_db.id
        resp = test_client.put(f"/api/v1/config/archival/{cid}", headers=auth_headers, json={"archival_days": 90})
        assert resp.status_code == 200
        assert resp.json()["archival_days"] == 90
    
    def test_delete_config(self, test_client, auth_headers, sample_archival_config_db):
        cid = sample_archival_config_db.id
        resp = test_client.delete(f"/api/v1/config/archival/{cid}", headers=auth_headers)
        assert resp.status_code == 204
    
    def test_create_requires_admin(self, test_client, user_auth_headers, sample_archival_config):
        resp = test_client.post("/api/v1/config/archival", headers=user_auth_headers, json=sample_archival_config)
        assert resp.status_code == 403
    
    def test_validates_deletion_days(self, test_client, auth_headers, sample_archival_config):
        cfg = sample_archival_config.copy()
        cfg["archival_days"] = 365
        cfg["deletion_days"] = 180
        resp = test_client.post("/api/v1/config/archival", headers=auth_headers, json=cfg)
        assert resp.status_code == 422
    
    def test_404_for_missing(self, test_client, auth_headers):
        assert test_client.get("/api/v1/config/archival/99999", headers=auth_headers).status_code == 404
