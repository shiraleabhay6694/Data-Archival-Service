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

