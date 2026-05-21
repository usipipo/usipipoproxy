"""API routes for VPN metrics."""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.application.services.metrics_service import MetricsService
from src.infrastructure.persistence.database import get_db

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def get_metrics_service(db: Session = Depends(get_db)) -> MetricsService:
    """Get metrics service instance."""
    return MetricsService(db)


@router.post("/agents/{server_id}")
def ingest_agent_metrics(
    server_id: uuid.UUID,
    metrics: dict,
    service: MetricsService = Depends(get_metrics_service),
):
    """Ingest metrics from a VPN agent.

    This endpoint is called by VPN agents every 1 minute to push metrics.

    **Authentication:** Requires X-API-Key header (agent API key)

    **Metrics payload:**
    ```json
    {
      "server_id": "uuid",
      "timestamp": "2026-03-28T10:00:00Z",
      "system": {
        "cpu_percent": 45.2,
        "memory_percent": 62.1,
        "disk_percent": 38.5,
        "network_rx_bytes": 1234567890,
        "network_tx_bytes": 9876543210
      },
      "vpn": {
        "wireguard": {
          "active_peers": 38,
          "total_bytes_transferred": 4500000000
        }
      },
      "latency_ms": {
        "avg": 12.5,
        "p95": 25.3,
        "p99": 45.8
      }
    }
    ```
    """
    try:
        service.ingest_agent_metrics(server_id, metrics)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}")
def get_server_metrics(
    server_id: uuid.UUID,
    from_date: datetime | None = Query(
        None,
        description="Start date (ISO format, defaults to 24 hours ago)",
    ),
    to_date: datetime | None = Query(
        None,
        description="End date (ISO format, defaults to now)",
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: MetricsService = Depends(get_metrics_service),
):
    """Get historical metrics for a server.

    Returns time-series metrics for a specific VPN server.
    """
    try:
        metrics = service.get_server_metrics(
            server_id=server_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/stats")
def get_server_stats(
    server_id: uuid.UUID,
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    service: MetricsService = Depends(get_metrics_service),
):
    """Get aggregated statistics for a server.

    Returns average CPU, memory, disk usage, total network transfer,
    average active connections, and average latency.
    """
    try:
        stats =         service.get_aggregated_stats(server_id=server_id, hours=hours)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{server_id}/health")
def check_agent_health(
    server_id: uuid.UUID,
    service: MetricsService = Depends(get_metrics_service),
):
    """Check if agent is healthy (heartbeat within last 2 minutes).

    Returns agent health status:
    - healthy: Heartbeat within last 2 minutes
    - degraded: Heartbeat between 2-5 minutes ago
    - unhealthy: No heartbeat in last 5 minutes or never
    """

    try:
        # Get recent metrics to check heartbeat
        metrics = service.get_server_metrics(
            server_id=server_id,
            limit=1,
        )

        if not metrics:
            return {
                "server_id": str(server_id),
                "status": "unhealthy",
                "message": "No metrics received yet",
            }

        last_metric_time = datetime.fromisoformat(metrics[0]["timestamp"])
        time_since = datetime.now(UTC) - last_metric_time

        if time_since < timedelta(minutes=2):
            status = "healthy"
            message = "Agent is healthy"
        elif time_since < timedelta(minutes=5):
            status = "degraded"
            message = "Agent heartbeat delayed"
        else:
            status = "unhealthy"
            message = "Agent heartbeat timeout"

        return {
            "server_id": str(server_id),
            "status": status,
            "message": message,
            "last_heartbeat": metrics[0]["timestamp"],
            "seconds_since_heartbeat": time_since.total_seconds(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/keys/{key_id}/usage")
def get_key_usage(
    user_id: uuid.UUID,
    key_id: str,
    service: MetricsService = Depends(get_metrics_service),
):
    """Get usage statistics for a user's VPN key.

    Returns bytes used, data limit, and percentage used.
    """
    try:
        usage =         service.get_user_key_usage(user_id=user_id, key_id=key_id)
        return usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
