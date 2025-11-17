"""Metrics retrieval routes."""

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()


@router.get("/{app_id}")
async def get_metrics(
    app_id: str,
    metric: Optional[str] = Query(None, regex="^(cpu|memory|requests|errors)$"),
    period: int = Query(3600, ge=60, le=604800)  # seconds
):
    """
    Get application metrics.
    
    - **app_id**: Application ID
    - **metric**: Specific metric (cpu, memory, requests, errors)
    - **period**: Time period in seconds (default: 1 hour)
    """
    
    # Mock metrics
    now = datetime.utcnow()
    metrics = []
    
    for i in range(10):
        timestamp = now - timedelta(minutes=i*5)
        metrics.append({
            "timestamp": timestamp.isoformat(),
            "cpu_usage_percent": 25.5 + (i * 2),
            "memory_usage_mb": 128 + (i * 10),
            "request_count": 1000 + (i * 50),
            "error_count": 5 + i,
        })
    
    metrics.reverse()
    
    return {
        "app_id": app_id,
        "period_seconds": period,
        "metrics": metrics
    }


@router.get("/{app_id}/cpu")
async def get_cpu_metrics(app_id: str, period: int = Query(3600)):
    """Get CPU usage metrics."""
    now = datetime.utcnow()
    data = []
    
    for i in range(12):
        timestamp = now - timedelta(minutes=i*5)
        data.append({
            "timestamp": timestamp.isoformat(),
            "cpu_percent": 20 + (i * 2)
        })
    
    return {
        "app_id": app_id,
        "metric": "cpu",
        "data": list(reversed(data))
    }


@router.get("/{app_id}/memory")
async def get_memory_metrics(app_id: str, period: int = Query(3600)):
    """Get memory usage metrics."""
    now = datetime.utcnow()
    data = []
    
    for i in range(12):
        timestamp = now - timedelta(minutes=i*5)
        data.append({
            "timestamp": timestamp.isoformat(),
            "memory_mb": 100 + (i * 5)
        })
    
    return {
        "app_id": app_id,
        "metric": "memory",
        "data": list(reversed(data))
    }


@router.get("/{app_id}/requests")
async def get_request_metrics(app_id: str, period: int = Query(3600)):
    """Get request metrics."""
    now = datetime.utcnow()
    data = []
    
    for i in range(12):
        timestamp = now - timedelta(minutes=i*5)
        data.append({
            "timestamp": timestamp.isoformat(),
            "requests": 500 + (i * 25),
            "errors": 2 + i
        })
    
    return {
        "app_id": app_id,
        "metric": "requests",
        "data": list(reversed(data))
    }


@router.get("/{app_id}/health")
async def get_health_status(app_id: str):
    """Get application health status."""
    return {
        "app_id": app_id,
        "status": "healthy",
        "uptime_seconds": 86400,
        "restarts": 0,
        "last_deployment": datetime.utcnow().isoformat()
    }
