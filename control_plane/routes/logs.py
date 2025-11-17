"""Log retrieval routes."""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

# Mock logs for demo
logs_db = {}


@router.get("/{app_id}")
async def get_logs(
    app_id: str,
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None, regex="^(DEBUG|INFO|WARNING|ERROR)$")
):
    """
    Get application logs.
    
    - **app_id**: Application ID
    - **limit**: Number of logs to return (default: 100)
    - **level**: Filter by log level (DEBUG, INFO, WARNING, ERROR)
    """
    
    # Mock logs
    logs = [
        {
            "id": "log_1",
            "app_id": app_id,
            "level": "INFO",
            "message": "Application started successfully",
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        },
        {
            "id": "log_2",
            "app_id": app_id,
            "level": "INFO",
            "message": "Server listening on port 8000",
            "timestamp": (datetime.utcnow() - timedelta(minutes=4)).isoformat()
        },
        {
            "id": "log_3",
            "app_id": app_id,
            "level": "DEBUG",
            "message": "Database connection established",
            "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat()
        },
    ]
    
    # Filter by level if provided
    if level:
        logs = [log for log in logs if log["level"] == level]
    
    return {
        "app_id": app_id,
        "total": len(logs),
        "logs": logs[:limit]
    }


@router.get("/{app_id}/deployment/{deployment_id}")
async def get_deployment_logs(
    app_id: str,
    deployment_id: str,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get logs for a specific deployment."""
    
    # Mock deployment logs
    logs = [
        {
            "id": "deploy_log_1",
            "deployment_id": deployment_id,
            "step": "Cloning repository",
            "message": "Repository cloned successfully",
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "id": "deploy_log_2",
            "deployment_id": deployment_id,
            "step": "Building Docker image",
            "message": "Building image with Python 3.9",
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    return {
        "deployment_id": deployment_id,
        "total": len(logs),
        "logs": logs[:limit]
    }


@router.get("/{app_id}/stream")
async def stream_logs(app_id: str):
    """Stream application logs in real-time (SSE)."""
    return {
        "message": "WebSocket streaming endpoint for real-time logs",
        "endpoint": f"/ws/logs/{app_id}"
    }
