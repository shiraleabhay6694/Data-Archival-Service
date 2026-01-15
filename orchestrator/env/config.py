from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="Data Archival Service - Orchestrator")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Server
    orchestrator_host: str = Field(default="0.0.0.0")
    orchestrator_port: int = Field(default=8000)
    
    # JWT
    jwt_secret_key: str = Field(default="change-this-secret-key-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)
    
    # Database
    orchestrator_db_host: str = Field(default="localhost")
    orchestrator_db_port: int = Field(default=3306)
    orchestrator_db_name: str = Field(default="archival_orchestrator")
    orchestrator_db_user: str = Field(default="root")
    orchestrator_db_password: str = Field(default="password")
    
    # Encryption (Fernet key)
    encryption_key: str = Field(default="your-32-byte-base64-encoded-key-here=")
    
    # Scheduler (cron)
    archival_job_cron: str = Field(default="* * * * *")
    purge_job_cron: str = Field(default="* * * * *")
    
    # Docker
    docker_socket: str = Field(default="/var/run/docker.sock")
    worker_image: str = Field(default="das-worker:latest")
    docker_network: str = Field(default="das-network")
    
    @property
    def database_url(self):
        return (
            f"mysql+pymysql://{self.orchestrator_db_user}:{self.orchestrator_db_password}"
            f"@{self.orchestrator_db_host}:{self.orchestrator_db_port}/{self.orchestrator_db_name}"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
