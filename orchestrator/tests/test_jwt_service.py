import pytest
from unittest.mock import patch, MagicMock
import sys


class TestJWTService:
    def test_create_and_verify_token(self):
        mock_settings = MagicMock()
        mock_settings.jwt_secret_key = "test-secret"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_expiration_hours = 24
        
        with patch.dict(sys.modules, {'orchestrator.env.config': MagicMock(settings=mock_settings)}):
            from orchestrator.security.jwt_service import JWTService
            svc = JWTService()
            svc.secret_key = mock_settings.jwt_secret_key
            svc.algorithm = mock_settings.jwt_algorithm
            svc.expiration_hours = mock_settings.jwt_expiration_hours
            
            result = svc.create_access_token("user", ["admin", "orders"])
            assert "access_token" in result
            
            payload = svc.verify_token(result["access_token"])
            assert payload["sub"] == "user"
            assert payload["roles"] == ["admin", "orders"]
    
    def test_invalid_token_returns_none(self):
        from orchestrator.security.jwt_service import JWTService
        svc = JWTService()
        assert svc.verify_token("invalid.token") is None
    
    def test_rbac_admin_access(self):
        from orchestrator.security.jwt_service import JWTService
        svc = JWTService()
        assert svc.check_role_permission(["admin"], "any_table")
        assert svc.check_role_permission(["orders"], "orders")
        assert not svc.check_role_permission(["orders"], "customers")
