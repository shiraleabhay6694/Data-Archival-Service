import pytest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


class TestAuth:
    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid")
        with patch('orchestrator.security.auth.jwt_service') as jwt:
            jwt.verify_token.return_value = {"sub": "user", "roles": ["admin"]}
            from orchestrator.security.auth import get_current_user
            result = await get_current_user(creds)
            assert result["sub"] == "user"
    
    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad")
        with patch('orchestrator.security.auth.jwt_service') as jwt:
            jwt.verify_token.return_value = None
            from orchestrator.security.auth import get_current_user
            with pytest.raises(HTTPException) as exc:
                await get_current_user(creds)
            assert exc.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_require_admin(self):
        from orchestrator.security.auth import require_admin
        assert (await require_admin({"sub": "admin", "roles": ["admin"]}))["sub"] == "admin"
        
        with pytest.raises(HTTPException) as exc:
            await require_admin({"sub": "user", "roles": ["orders"]})
        assert exc.value.status_code == 403


class TestAuthFlow:
    def test_token_endpoint(self, test_client):
        resp = test_client.post("/api/v1/auth/token", json={"username": "user", "roles": ["admin"]})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
    
    def test_protected_requires_token(self, test_client):
        assert test_client.get("/api/v1/config/archival").status_code == 403
    
    def test_protected_accepts_valid_token(self, test_client, auth_headers):
        assert test_client.get("/api/v1/config/archival", headers=auth_headers).status_code == 200
