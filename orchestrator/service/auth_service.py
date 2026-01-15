from typing import List
from orchestrator.security.jwt_service import jwt_service
import logging

logger = logging.getLogger(__name__)


class AuthService:
    
    def create_token(self, username: str, roles: List[str]) -> dict:
        token_data = jwt_service.create_access_token(
            username=username,
            roles=roles
        )
        logger.info(f"Token created for {username}")
        return token_data
    
    def check_role_permission(self, roles: List[str], table_name: str) -> bool:
        return jwt_service.check_role_permission(roles, table_name)
    
    def is_admin(self, roles: List[str]) -> bool:
        return "admin" in roles


# Global auth service instance
auth_service = AuthService()
