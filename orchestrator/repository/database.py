from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orchestrator.env.config import settings
from orchestrator.model.models import Base

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.log_level == "DEBUG"
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
