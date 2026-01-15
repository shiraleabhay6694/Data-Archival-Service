from cryptography.fernet import Fernet
from orchestrator.env.config import settings
import base64
import hashlib


class EncryptionService:
    
    def __init__(self):
        key = settings.encryption_key
        # Fernet needs 32 url-safe base64-encoded bytes
        if len(key) < 32:
            key = hashlib.sha256(key.encode()).digest()
            key = base64.urlsafe_b64encode(key)
        else:
            try:
                self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
                return
            except Exception:
                key = hashlib.sha256(key.encode()).digest()
                key = base64.urlsafe_b64encode(key)
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


encryption_service = EncryptionService()
