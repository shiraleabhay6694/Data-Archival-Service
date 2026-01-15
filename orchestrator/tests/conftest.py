import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def mock_settings():
    s = MagicMock()
    s.jwt_secret_key = "test-secret"
    s.jwt_algorithm = "HS256"
    s.jwt_expiration_hours = 24
    s.database_url = "sqlite:///:memory:"
    s.app_name = "Test"
    s.app_version = "1.0"
    s.log_level = "INFO"
    s.orchestrator_host = "0.0.0.0"
    s.orchestrator_port = 8000
    return s


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    return engine


@pytest.fixture
def db_session(db_engine):
    from orchestrator.model.models import Base
    Base.metadata.create_all(db_engine)
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_client(db_session, db_engine):
    from orchestrator.model.models import Base
    Base.metadata.create_all(db_engine)
    
    with patch('orchestrator.repository.database.engine', db_engine):
        with patch('orchestrator.scheduler.scheduler_service.scheduler_service') as mock_sched:
            mock_sched.start = MagicMock()
            mock_sched.stop = MagicMock()
            mock_sched.get_job_status = MagicMock(return_value={
                'archival_jobs': {'enabled': True, 'running': False, 'next_run': None},
                'purge_jobs': {'enabled': True, 'running': False, 'next_run': None}
            })
            
            with patch('orchestrator.main.init_db'):
                with patch('orchestrator.main.scheduler_service', mock_sched):
                    from orchestrator.main import app
                    from orchestrator.repository.database import get_db
                    from fastapi.testclient import TestClient
                    
                    def override():
                        yield db_session
                    
                    app.dependency_overrides[get_db] = override
                    with TestClient(app) as client:
                        yield client
                    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(test_client):
    resp = test_client.post("/api/v1/auth/token", json={"username": "admin", "roles": ["admin"]})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_headers(test_client):
    resp = test_client.post("/api/v1/auth/token", json={"username": "user", "roles": ["orders"]})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_archival_config():
    return {
        "primary_db_host": "primary-db",
        "primary_db_port": 3306,
        "primary_db_name": "production",
        "primary_db_user": "root",
        "primary_db_password": "secret",
        "archival_db_host": "archival-db",
        "archival_db_port": 3306,
        "archival_db_name": "archival",
        "archival_db_user": "root",
        "archival_db_password": "secret",
        "table_name": "test_orders",
        "date_column": "created_at",
        "archival_days": 180,
        "deletion_days": 730,
        "enabled": True
    }


@pytest.fixture
def sample_archival_config_db(db_session):
    from orchestrator.model.models import ArchivalConfig
    from orchestrator.security.encryption_service import encryption_service
    cfg = ArchivalConfig(
        primary_db_host="primary-db",
        primary_db_port=3306,
        primary_db_name="production",
        primary_db_user_encrypted=encryption_service.encrypt("root"),
        primary_db_password_encrypted=encryption_service.encrypt("secret"),
        archival_db_host="archival-db",
        archival_db_port=3306,
        archival_db_name="archival",
        archival_db_user_encrypted=encryption_service.encrypt("root"),
        archival_db_password_encrypted=encryption_service.encrypt("secret"),
        table_name="orders",
        date_column="created_at",
        archival_days=180,
        deletion_days=730,
        enabled=True
    )
    db_session.add(cfg)
    db_session.commit()
    db_session.refresh(cfg)
    return cfg
