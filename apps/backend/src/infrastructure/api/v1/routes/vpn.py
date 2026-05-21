"""Routes para gestion de claves VPN."""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from usipipo_commons.domain.entities.server import Server
from usipipo_commons.domain.entities.user import User

from src.core.application.services.metrics_service import MetricsService
from src.core.application.services.server_registry_service import ServerRegistryService
from src.core.application.services.vpn_service import VpnService
from src.infrastructure.api.v1.deps import get_current_user, get_db, get_vpn_service
from src.shared.schemas.vpn import (
    CreateVpnKeyRequest,
    UpdateVpnKeyRequest,
    VpnKeyResponse,
    VpnServerResponse,
    VpnServersListResponse,
)

router = APIRouter(prefix="/vpn", tags=["VPN Keys"])


def get_server_registry_service(
    db: Session = Depends(get_db),
) -> ServerRegistryService:
    """
    Dependency para obtener ServerRegistryService.

    Args:
        db: Sesión de base de datos

    Returns:
        ServerRegistryService: Servicio de registro de servidores
    """
    return ServerRegistryService(db)


@router.get(
    "/keys",
    response_model=list[VpnKeyResponse],
    status_code=status.HTTP_200_OK,
)
def list_vpn_keys(
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
    server_registry: ServerRegistryService = Depends(get_server_registry_service),
):
    """
    Lista todas las claves VPN del usuario.

    Args:
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        List[VpnKeyResponse]: Lista de claves VPN
    """
    keys = vpn_service.get_user_keys(current_user.id)

    # Build server name cache
    server_names: dict[UUID, str | None] = {}
    for key in keys:
        if key.server_id and key.server_id not in server_names:
            server = server_registry.get_server(key.server_id)
            server_names[key.server_id] = server.name if server else None

    # Mapear entidades a schema de respuesta
    return [
        VpnKeyResponse(
            id=key.id,
            user_id=key.user_id,
            server_id=key.server_id,
            server_name=server_names.get(key.server_id) if key.server_id else None,
            name=key.name,
            key_type=key.key_type,
            config=key.key_data,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_seen_at,
            data_used_gb=key.used_gb,
            data_limit_gb=key.data_limit_gb,
        )
        for key in keys
    ]


@router.post(
    "/keys",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vpn_key(
    request: CreateVpnKeyRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
    server_registry: ServerRegistryService = Depends(get_server_registry_service),
):
    """
    Crea una nueva clave VPN.

    Args:
        request: Solicitud para crear clave VPN
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Clave VPN creada

    Raises:
        HTTPException: 400 si hay error en la creación
    """
    try:
        key = vpn_service.create_key(
            user_id=current_user.id,
            name=request.name,
            vpn_type=request.vpn_type.value,
            data_limit_gb=request.data_limit_gb,
            server_id=request.server_id,
        )

        # Fetch server name
        server_name: str | None = None
        if key.server_id:
            server = server_registry.get_server(key.server_id)
            if server:
                server_name = server.name

        # Mapear entidad a schema de respuesta
        return VpnKeyResponse(
            id=key.id,
            user_id=key.user_id,
            server_id=key.server_id,
            server_name=server_name,
            name=key.name,
            key_type=key.key_type,
            config=key.key_data,
            deeplink="",
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_seen_at,
            data_used_gb=key.used_gb,
            data_limit_gb=key.data_limit_gb,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create key: {str(e)}",
        )


@router.get(
    "/keys/{key_id}",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_200_OK,
)
def get_vpn_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
    server_registry: ServerRegistryService = Depends(get_server_registry_service),
):
    """
    Obtiene detalles de una clave VPN.

    Args:
        key_id: UUID de la clave
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Detalles de la clave

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    key = vpn_service.get_key_by_id(key_id)

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found",
        )

    if key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this key",
        )

    # Fetch server name
    server_name: str | None = None
    if key.server_id:
        server = server_registry.get_server(key.server_id)
        if server:
            server_name = server.name

    return VpnKeyResponse(
        id=key.id,
        user_id=key.user_id,
        server_id=key.server_id,
        server_name=server_name,
        name=key.name,
        key_type=key.key_type,
        config=key.key_data,
        deeplink="",
        created_at=key.created_at,
        expires_at=key.expires_at,
        last_used_at=key.last_seen_at,
        data_used_gb=key.used_gb,
        data_limit_gb=key.data_limit_gb,
    )


@router.delete(
    "/keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vpn_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
):
    """
    Elimina una clave VPN.

    Args:
        key_id: UUID de la clave
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    try:
        vpn_service.delete_key(current_user.id, key_id)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this key",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete key: {str(e)}",
        )


@router.put(
    "/keys/{key_id}",
    response_model=VpnKeyResponse,
    status_code=status.HTTP_200_OK,
)
def update_vpn_key(
    key_id: UUID,
    request: UpdateVpnKeyRequest,
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
    server_registry: ServerRegistryService = Depends(get_server_registry_service),
):
    """
    Actualiza una clave VPN.

    Args:
        key_id: UUID de la clave
        request: Solicitud de actualización
        current_user: Usuario autenticado
        vpn_service: Servicio de VPN

    Returns:
        VpnKeyResponse: Clave VPN actualizada

    Raises:
        HTTPException: 404 si no existe, 403 si no está autorizado
    """
    try:
        key = vpn_service.update_key(
            user_id=current_user.id,
            key_id=key_id,
            name=request.name,
            data_limit_gb=request.data_limit_gb,
        )

        # Fetch server name
        server_name: str | None = None
        if key.server_id:
            server = server_registry.get_server(key.server_id)
            if server:
                server_name = server.name

        return VpnKeyResponse(
            id=key.id,
            user_id=key.user_id,
            server_id=key.server_id,
            server_name=server_name,
            name=key.name,
            key_type=key.key_type,
            config=key.key_data,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_seen_at,
            data_used_gb=key.used_gb,
            data_limit_gb=key.data_limit_gb,
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this key",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update key: {str(e)}",
        )


@router.get(
    "/servers",
    response_model=VpnServersListResponse,
    status_code=status.HTTP_200_OK,
    tags=["VPN Servers"],
)
def get_available_servers(
    protocol: str | None = Query(
        None,
        description="Protocol type (wireguard). Returns all if not specified.",
    ),
    current_user: User = Depends(get_current_user),
    server_service: ServerRegistryService = Depends(get_server_registry_service),
) -> VpnServersListResponse:
    """
    Get list of available VPN servers for user selection.

    Args:
        protocol: Optional protocol filter. If not specified, returns all servers.
        current_user: Authenticated user
        server_service: Server registry service

    Returns:
        VpnServersListResponse: List of servers with load indicators

    Raises:
        HTTPException: 400 if protocol is invalid
    """
    # Get all available servers
    if protocol is not None:
        # Validate protocol (wireguard only)
        if protocol.lower() != "wireguard":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid protocol. Only 'wireguard' is supported.",
            )
        all_servers = server_service.get_servers_for_user("wireguard")
    else:
        # Get all WireGuard servers
        all_servers = server_service.get_servers_for_user("wireguard")

    # Get top 5 recommended (lowest load)
    recommended_servers = all_servers[:5]

    # Convert to response schema
    def to_response(server: Server) -> VpnServerResponse:
        load_pct = int((server.current_connections / max(server.max_connections, 1)) * 100)

        return VpnServerResponse(
            id=server.id,
            name=server.name,
            country_code=server.country_code,
            country_name=server.country_name,
            city=server.city,
            load_percentage=load_pct,
            status=server.status,
        )

    return VpnServersListResponse(
        servers=[to_response(s) for s in all_servers],
        recommended=[to_response(s) for s in recommended_servers],
    )


def get_metrics_service(
    db: Session = Depends(get_db),
) -> MetricsService:
    """Dependency to get MetricsService instance."""
    return MetricsService(db)


def parse_time_range(since: str) -> timedelta:
    """Parse a time range string into a timedelta.

    Args:
        since: Time range string (e.g., "1h", "24h", "7d", "30d")

    Returns:
        Timedelta representing the time range

    Raises:
        ValueError: If the time range format is invalid
    """
    if since.endswith("h"):
        try:
            hours = int(since[:-1])
            return timedelta(hours=hours)
        except ValueError:
            raise ValueError(f"Invalid time range: {since}")
    elif since.endswith("d"):
        try:
            days = int(since[:-1])
            return timedelta(days=days)
        except ValueError:
            raise ValueError(f"Invalid time range: {since}")
    else:
        raise ValueError(f"Invalid time range format: {since}. Use '1h', '24h', '7d', or '30d'")


# ---------------------------------------------------------------------------
# WireGuard Metrics Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/servers/{server_id}/wireguard/metrics",
    status_code=status.HTTP_200_OK,
    tags=["WireGuard Metrics"],
)
def get_wireguard_metrics(
    server_id: UUID,
    since: str = Query(
        default="24h",
        pattern=r"^\d+[hd]$",
        description="Time range: 1h, 24h, 7d, 30d",
    ),
    current_user: User = Depends(get_current_user),
    vpn_service: VpnService = Depends(get_vpn_service),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    """
    Get historical WireGuard metrics for a server with time-series data.

    Requires the user to have at least one VPN key on this server.

    Args:
        server_id: UUID of the VPN server
        since: Time range (1h, 24h, 7d, 30d). Default: 24h
        current_user: Authenticated user
        vpn_service: VPN service for authorization check
        metrics_service: Metrics service for data retrieval

    Returns:
        Dict with WireGuard metrics time-series and summary

    Raises:
        HTTPException: 400 if invalid time range, 403 if not authorized,
                       404 if no metrics found
    """
    # Validate time range
    try:
        parse_time_range(since)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Authorization: user must have VPN keys on this server
    user_keys = vpn_service.get_user_keys_for_server(
        user_id=current_user.id,
        server_id=server_id,
    )
    if not user_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have any VPN keys on this server",
        )

    # Get historical WireGuard metrics
    raw_metrics = metrics_service.get_wireguard_metrics_by_range(
        server_id=server_id,
        since=since,
    )

    if not raw_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No WireGuard metrics found for this server in the last {since}",
        )

    # Build time series points
    time_series = [
        {
            "timestamp": m.get("timestamp", ""),
            "peer_count": m.get("peer_count"),
            "connected_peers": 1 if m.get("is_connected") else 0,
            "total_bytes_rx": m.get("bytes_received"),
            "total_bytes_tx": m.get("bytes_sent"),
        }
        for m in raw_metrics
    ]

    # Calculate summary
    avg_peers = (
        sum(m.get("peer_count") or 0 for m in raw_metrics) / len(raw_metrics)
        if raw_metrics
        else None
    )
    total_bytes = max(
        ((m.get("bytes_received") or 0) + (m.get("bytes_sent") or 0) for m in raw_metrics),
        default=None,
    )

    summary = {
        "avg_peer_count": avg_peers,
        "total_bytes_transferred": total_bytes,
        "data_points": len(raw_metrics),
        "time_range": since,
    }

    return {
        "server_id": server_id,
        "time_range": since,
        "time_series": time_series,
        "summary": summary,
    }
