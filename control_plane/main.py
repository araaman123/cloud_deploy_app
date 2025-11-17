"""
DevOps Automation SaaS - Main Control Plane API

This is the core FastAPI application that manages:
- User authentication (GitHub OAuth)
- Application deployment management
- Infrastructure provisioning
- Logs and metrics retrieval
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add control_plane to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from database.init import init_db
from routes import auth, apps, deployments, logs, metrics
from middleware import error_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting DevOps Automation SaaS Control Plane...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    logger.info("Shutting down Control Plane...")


# Create FastAPI app
app = FastAPI(
    title="DevOps Automation SaaS",
    description="Platform to deploy backend apps automatically to Kubernetes",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
app.add_exception_handler(Exception, error_handler.exception_handler)


@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is healthy."""
    return {
        "status": "healthy",
        "service": "DevOps Automation SaaS Control Plane",
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(apps.router, prefix="/api/v1/apps", tags=["Applications"])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["Deployments"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])

# Mount static files
try:
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API documentation link."""
    return {
        "message": "DevOps Automation SaaS API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "ui": "/ui"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
