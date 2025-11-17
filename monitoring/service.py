"""Monitoring service for the control plane."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/prometheus/stats")
async def get_prometheus_stats():
    """Get Prometheus statistics."""
    return {
        "prometheus_url": "http://prometheus:9090",
        "metrics_collected": [
            "node_cpu_seconds_total",
            "node_memory_MemAvailable_bytes",
            "container_cpu_usage_seconds_total",
            "container_memory_usage_bytes",
            "http_requests_total",
            "http_request_duration_seconds"
        ]
    }


@router.get("/grafana/dashboards")
async def get_grafana_dashboards():
    """Get available Grafana dashboards."""
    return {
        "grafana_url": "http://grafana:3000",
        "dashboards": [
            {
                "name": "Cluster Overview",
                "description": "Overall cluster metrics",
                "tags": ["cluster", "overview"]
            },
            {
                "name": "Application Performance",
                "description": "Per-application metrics",
                "tags": ["application", "performance"]
            },
            {
                "name": "Resource Usage",
                "description": "CPU, memory, network usage",
                "tags": ["resources"]
            },
            {
                "name": "Pod Metrics",
                "description": "Individual pod metrics",
                "tags": ["pod", "containers"]
            }
        ]
    }
