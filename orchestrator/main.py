from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from orchestrator.env.config import settings
from orchestrator.repository.database import init_db
from orchestrator.scheduler.scheduler_service import scheduler_service
from orchestrator.router import auth_router, config_router, archive_router
from orchestrator.router.schema.common import HealthResponse

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting orchestrator service...")
    init_db()
    scheduler_service.start()
    logger.info("Orchestrator ready")
    
    yield
    
    logger.info("Shutting down...")
    scheduler_service.stop()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Data archival service for MySQL databases with scheduled jobs and RBAC.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(config_router)
app.include_router(archive_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Data Archival Service - Orchestrator",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="orchestrator",
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "orchestrator.main:app",
        host=settings.orchestrator_host,
        port=settings.orchestrator_port,
        reload=False
    )
