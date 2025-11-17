"""Application management routes."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import Application, AppType as AppTypeEnum
from database.init import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CreateAppRequest(BaseModel):
    app_name: str
    repo_url: str
    runtime: str = "python"
    branch: str = "main"


@router.post("")
async def create_app(request: CreateAppRequest, db: Session = Depends(get_db)):
    """Create a new deployment."""
    if not request.app_name or not request.repo_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="App name and repo URL are required"
        )
    
    if request.runtime not in ["python", "node", "static"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid runtime. Must be: python, node, or static"
        )
    
    app_id = str(uuid.uuid4())
    namespace = f"app-{app_id[:8]}"
    domain = f"{request.app_name.lower()}.apps.local"
    
    app_type_map = {
        "python": AppTypeEnum.PYTHON,
        "node": AppTypeEnum.NODE,
        "static": AppTypeEnum.STATIC
    }
    
    app = Application(
        id=app_id,
        name=request.app_name,
        github_repo_url=request.repo_url,
        github_branch=request.branch,
        app_type=app_type_map[request.runtime],
        status="pending",
        namespace=namespace,
        domain=domain,
        tls_enabled=True
    )
    
    db.add(app)
    db.commit()
    db.refresh(app)
    
    return {
        "message": "Application created successfully",
        "app": {
            "id": app.id,
            "name": app.name,
            "github_repo_url": app.github_repo_url,
            "github_branch": app.github_branch,
            "app_type": app.app_type.value if app.app_type else None,
            "status": app.status,
            "namespace": app.namespace,
            "domain": app.domain,
            "tls_enabled": app.tls_enabled,
            "created_at": app.created_at.isoformat()
        }
    }


@router.get("")
async def list_apps(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """List all deployments."""
    apps = db.query(Application).offset(skip).limit(limit).all()
    total = db.query(Application).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "apps": [
            {
                "id": app.id,
                "name": app.name,
                "github_repo_url": app.github_repo_url,
                "github_branch": app.github_branch,
                "app_type": app.app_type.value if app.app_type else None,
                "status": app.status,
                "namespace": app.namespace,
                "domain": app.domain,
                "created_at": app.created_at.isoformat()
            }
            for app in apps
        ]
    }


@router.get("/{app_id}")
async def get_app(app_id: str, db: Session = Depends(get_db)):
    """Get deployment details."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    return {
        "id": app.id,
        "name": app.name,
        "github_repo_url": app.github_repo_url,
        "github_branch": app.github_branch,
        "app_type": app.app_type.value if app.app_type else None,
        "status": app.status,
        "namespace": app.namespace,
        "domain": app.domain,
        "created_at": app.created_at.isoformat()
    }


@router.delete("/{app_id}")
async def delete_app(app_id: str, db: Session = Depends(get_db)):
    """Delete a deployment."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    db.delete(app)
    db.commit()
    
    return {
        "message": "Application deleted successfully",
        "app_id": app_id
    }


@router.patch("/{app_id}")
async def update_app(
    app_id: str,
    name: Optional[str] = None,
    github_branch: Optional[str] = None,
    cpu_limit: Optional[str] = None,
    memory_limit: Optional[str] = None,
    replicas: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Update application configuration."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    if name:
        app.name = name
    if github_branch:
        app.github_branch = github_branch
    if cpu_limit:
        app.cpu_limit = cpu_limit
    if memory_limit:
        app.memory_limit = memory_limit
    if replicas:
        app.replicas = replicas
    
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    return {
        "message": "Application updated successfully",
        "app": {
            "id": app.id,
            "name": app.name,
            "github_repo_url": app.github_repo_url,
            "github_branch": app.github_branch,
            "app_type": app.app_type.value if app.app_type else None,
            "status": app.status,
            "updated_at": app.updated_at.isoformat()
        }
    }
