"""Deployment management routes."""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import sys
from pathlib import Path
import asyncio

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import Deployment, Application
from database.init import SessionLocal
from services.deployment_orchestrator import start_deployment

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/trigger")
async def trigger_deployment_generic(app_id: str = Query(...), commit_hash: str = Query("main"), db: Session = Depends(get_db)):
    """Trigger a new deployment (generic endpoint)."""
    # Check if app exists
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    deployment_id = str(uuid.uuid4())
    
    deployment = Deployment(
        id=deployment_id,
        app_id=app_id,
        status="pending",
        commit_hash=commit_hash
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    # Start deployment in background
    asyncio.create_task(start_deployment(deployment_id, app_id))
    
    return {
        "message": "Deployment triggered successfully",
        "deployment_id": deployment.id,
        "app_id": deployment.app_id,
        "status": deployment.status,
        "commit_hash": deployment.commit_hash
    }


@router.post("/{app_id}/trigger")
async def trigger_deployment(app_id: str, commit_hash: str = Query("latest"), db: Session = Depends(get_db)):
    """Trigger a new deployment."""
    # Check if app exists
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    deployment_id = str(uuid.uuid4())
    
    deployment = Deployment(
        id=deployment_id,
        app_id=app_id,
        status="pending",
        commit_hash=commit_hash
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    # Start deployment in background
    asyncio.create_task(start_deployment(deployment_id, app_id))
    
    return {
        "message": "Deployment triggered successfully",
        "deployment": {
            "id": deployment.id,
            "app_id": deployment.app_id,
            "status": deployment.status,
            "commit_hash": deployment.commit_hash,
            "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
            "steps": [
                {"name": "Cloning repository", "status": "pending"},
                {"name": "Detecting app type", "status": "pending"},
                {"name": "Building Docker image", "status": "pending"},
                {"name": "Pushing to registry", "status": "pending"},
                {"name": "Creating Kubernetes namespace", "status": "pending"},
                {"name": "Deploying application", "status": "pending"},
                {"name": "Configuring TLS", "status": "pending"},
            ]
        }
    }


@router.get("/{deployment_id}")
async def get_deployment(deployment_id: str, db: Session = Depends(get_db)):
    """Get deployment status."""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found"
        )
    
    return {
        "id": deployment.id,
        "app_id": deployment.app_id,
        "status": deployment.status,
        "commit_hash": deployment.commit_hash,
        "started_at": deployment.started_at.isoformat() if deployment.started_at else None,
        "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None,
        "error_message": deployment.error_message
    }


@router.post("/{deployment_id}/retry")
async def retry_deployment(deployment_id: str, db: Session = Depends(get_db)):
    """Retry a failed deployment."""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found"
        )
    
    deployment.status = "pending"
    deployment.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(deployment)
    
    return {
        "message": "Deployment retry initiated",
        "deployment": {
            "id": deployment.id,
            "app_id": deployment.app_id,
            "status": deployment.status,
            "started_at": deployment.started_at.isoformat()
        }
    }


@router.post("/{deployment_id}/cancel")
async def cancel_deployment(deployment_id: str, db: Session = Depends(get_db)):
    """Cancel a running deployment."""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found"
        )
    
    deployment.status = "cancelled"
    
    db.commit()
    db.refresh(deployment)
    
    return {
        "message": "Deployment cancelled",
        "deployment": {
            "id": deployment.id,
            "app_id": deployment.app_id,
            "status": deployment.status
        }
    }
