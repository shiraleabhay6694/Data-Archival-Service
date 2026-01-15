from pydantic import BaseModel
from typing import List


class CreateTokenRequest(BaseModel):
    username: str
    roles: List[str] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
