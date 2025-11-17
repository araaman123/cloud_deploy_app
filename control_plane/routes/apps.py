"""Application management routes."""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

apps_db = {}


class CreateAppRequest(BaseModel):
    app_name: str
    repo_url: str
    runtime: str = "python"
    branch: str = "main"


@router.post("")
async def create_app(request: CreateAppRequest):
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
    
    app = {
        "id": app_id,
        "name": request.app_name,
        "github_repo_url": request.repo_url,
        "github_branch": request.branch,
        "app_type": request.runtime,
        "status": "pending",
        "namespace": namespace,
        "domain": domain,
        "tls_enabled": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    apps_db[app_id] = app
    
    return {
        "message": "Application created successfully",
        "app": app
    }


@router.get("")
async def list_apps(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """List all deployments."""
    apps_list = list(apps_db.values())
    return {
        "total": len(apps_list),
        "skip": skip,
        "limit": limit,
        "apps": apps_list[skip:skip+limit]
    }


@router.get("/{app_id}")
async def get_app(app_id: str):
    """Get deployment details."""
    if app_id not in apps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    return apps_db[app_id]


@router.delete("/{app_id}")
async def delete_app(app_id: str):
    """Delete a deployment."""
    if app_id not in apps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    deleted_app = apps_db.pop(app_id)
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
    replicas: Optional[int] = None
):
    """Update application configuration."""
    if app_id not in apps_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {app_id} not found"
        )
    
    app = apps_db[app_id]
    
    if name:
        app["name"] = name
    if github_branch:
        app["github_branch"] = github_branch
    if cpu_limit:
        app["cpu_limit"] = cpu_limit
    if memory_limit:
        app["memory_limit"] = memory_limit
    if replicas:
        app["replicas"] = replicas
    
    app["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": "Application updated successfully",
        "app": app
    }
