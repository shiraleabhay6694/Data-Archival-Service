from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from orchestrator.env.config import settings


class JWTService:
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expiration_hours = settings.jwt_expiration_hours
    
    def create_access_token(self, username: str, roles: List[str]):
        expire = datetime.utcnow() + timedelta(hours=self.expiration_hours)
        
        token = jwt.encode({
            "sub": username,
            "roles": roles,
            "exp": expire,
            "iat": datetime.utcnow()
        }, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.expiration_hours * 3600
        }
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            return None
    
    def check_role_permission(self, user_roles: List[str], required_table: str) -> bool:
        return "admin" in user_roles or required_table in user_roles


jwt_service = JWTService()
