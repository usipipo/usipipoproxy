"""Service for ingesting and querying VPN agent metrics."""

import uuid
from datetime import UTC, datetime, timedelta

from loguru import logger
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models.server_metric_model import ServerMetricModel
from src.infrastructure.persistence.models.wireguard_metric_model import WireGuardMetricModel


class MetricsService:
    """Service for ingesting and querying VPN agent metrics.

    This service handles:
    - Ingesting metrics from VPN agents (pushed every 1 minute)
    - Storing metrics in time-series database
    - Querying historical metrics for dashboards
    - Computing aggregated statistics
    """

    def __init__(self, session: Session):
        """Initialize metrics service.

        Args:
            session: Async database session
        """
        self.session = session
        logger.info("MetricsService initialized")

    def ingest_agent_metrics(
        self,
        server_id: uuid.UUID,
        metrics: dict,
    ) -> None:
        """Ingest metrics from a VPN agent.

        Called by agents every 1 minute to push metrics.

        Args:
            server_id: UUID of the server sending metrics
            metrics: Metrics payload from agent

        Raises:
            ValueError: If metrics contain invalid values
        """
        try:
            # Validate and extract metrics with range checks
            system = metrics.get("system", {})
            vpn = metrics.get("vpn", {})
            latency = metrics.get("latency_ms", {})

            # Validate CPU (0-100%)
            cpu_percent = system.get("cpu_percent")
            if cpu_percent is not None and not (0 <= cpu_percent <= 100):
                raise ValueError(f"Invalid CPU percent: {cpu_percent}")

            # Validate memory (0-100%)
            memory_percent = system.get("memory_percent")
            if memory_percent is not None and not (0 <= memory_percent <= 100):
                raise ValueError(f"Invalid memory percent: {memory_percent}")

            # Validate disk (0-100%)
            disk_percent = system.get("disk_percent")
            if disk_percent is not None and not (0 <= disk_percent <= 100):
                raise ValueError(f"Invalid disk percent: {disk_percent}")

            # Validate non-negative values
            network_rx = system.get("network_rx_bytes", 0)
            network_tx = system.get("network_tx_bytes", 0)
            if network_rx < 0 or network_tx < 0:
                raise ValueError("Network bytes cannot be negative")

            wg_peers = vpn.get("wireguard", {}).get("active_peers", 0)
            if wg_peers < 0:
                raise ValueError("Active connections cannot be negative")

            # Validate latency (non-negative)
            latency_avg = latency.get("avg")
            if latency_avg is not None and latency_avg < 0:
                raise ValueError(f"Invalid latency: {latency_avg}")

            # Parse timestamp
            timestamp = datetime.fromisoformat(metrics.get("timestamp", datetime.now().isoformat()))

            # Create ServerMetricModel record
            server_metric = ServerMetricModel(
                server_id=server_id,
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                wireguard_active_peers=wg_peers,
                total_bytes_transferred=vpn.get("wireguard", {}).get("total_bytes_transferred", 0),
                latency_avg_ms=latency_avg,
                latency_p95_ms=latency.get("p95"),
                latency_p99_ms=latency.get("p99"),
            )

            self.session.add(server_metric)

            # Extract and store WireGuard-specific metrics from top-level 'wireguard' key
            wireguard_data = metrics.get("wireguard", {})
            if wireguard_data:
                try:
                    # WireGuard metrics are aggregated - store as a single record per collection
                    wg_metric = WireGuardMetricModel(
                        id=str(uuid.uuid4()),
                        server_id=str(server_id),
                        timestamp=timestamp,
                        peer_public_key="aggregated",  # Special key for aggregated metrics
                        bytes_received=wireguard_data.get("total_bytes_rx", 0),
                        bytes_sent=wireguard_data.get("total_bytes_tx", 0),
                        last_handshake=self._parse_optional_datetime(
                            wireguard_data.get("last_handshake")
                        ),
                        is_connected=wireguard_data.get("connected_peers", 0) > 0,
                    )
                    self.session.add(wg_metric)
                    logger.info(
                        f"Ingested WireGuard metrics for server {server_id}: "
                        f"peers={wireguard_data.get('peer_count', 0)}, "
                        f"connected={wireguard_data.get('connected_peers', 0)}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to extract WireGuard metrics for server {server_id}: {e}. "
                        f"ServerMetricModel was still saved successfully."
                    )

            self.session.commit()

            logger.debug(f"Ingested metrics for server {server_id}")

        except ValueError as e:
            logger.warning(f"Invalid metrics received from server {server_id}: {e}")
            self.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to ingest metrics for server {server_id}: {e}")
            self.session.rollback()
            raise

    @staticmethod
    def _parse_optional_datetime(value: str | None) -> datetime | None:
        """Parse an optional ISO format datetime string.

        Args:
            value: ISO format datetime string or None

        Returns:
            Parsed datetime or None
        """
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None

    def get_server_metrics(
        self,
        server_id: uuid.UUID,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get historical metrics for a server.

        Args:
            server_id: UUID of the server
            from_date: Start date (optional, defaults to 24 hours ago)
            to_date: End date (optional, defaults to now)
            limit: Maximum number of records to return

        Returns:
            List of metric dictionaries
        """
        try:
            if from_date is None:
                from_date = datetime.now() - timedelta(hours=24)
            if to_date is None:
                to_date = datetime.now()

            query = (
                select(ServerMetricModel)
                .where(ServerMetricModel.server_id == server_id)
                .where(ServerMetricModel.timestamp >= from_date)
                .where(ServerMetricModel.timestamp <= to_date)
                .order_by(desc(ServerMetricModel.timestamp))
                .limit(limit)
            )

            result = self.session.execute(query)
            metrics = result.scalars().all()

            return [
                {
                    "id": m.id,
                    "server_id": m.server_id,
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": float(m.cpu_percent) if m.cpu_percent else None,
                    "memory_percent": float(m.memory_percent) if m.memory_percent else None,
                    "disk_percent": float(m.disk_percent) if m.disk_percent else None,
                    "network_rx_bytes": m.network_rx_bytes,
                    "network_tx_bytes": m.network_tx_bytes,
                    "wireguard_active_peers": m.wireguard_active_peers,
                    "total_bytes_transferred": m.total_bytes_transferred,
                    "latency_avg_ms": float(m.latency_avg_ms) if m.latency_avg_ms else None,
                    "latency_p95_ms": float(m.latency_p95_ms) if m.latency_p95_ms else None,
                    "latency_p99_ms": float(m.latency_p99_ms) if m.latency_p99_ms else None,
                }
                for m in metrics
            ]

        except Exception as e:
            logger.error(f"Failed to get metrics for server {server_id}: {e}")
            raise

    def get_aggregated_stats(
        self,
        server_id: uuid.UUID,
        hours: int = 24,
    ) -> dict:
        """Get aggregated statistics for a server.

        Args:
            server_id: UUID of the server
            hours: Time window in hours

        Returns:
            Dictionary with aggregated stats
        """
        try:
            from_date = datetime.now() - timedelta(hours=hours)

            query = (
                select(
                    func.avg(ServerMetricModel.cpu_percent).label("avg_cpu"),
                    func.avg(ServerMetricModel.memory_percent).label("avg_memory"),
                    func.avg(ServerMetricModel.disk_percent).label("avg_disk"),
                    func.sum(ServerMetricModel.network_rx_bytes).label("total_rx"),
                    func.sum(ServerMetricModel.network_tx_bytes).label("total_tx"),
                    func.avg(ServerMetricModel.wireguard_active_peers).label("avg_wg_peers"),
                    func.avg(ServerMetricModel.latency_avg_ms).label("avg_latency"),
                )
                .where(ServerMetricModel.server_id == server_id)
                .where(ServerMetricModel.timestamp >= from_date)
            )

            result = self.session.execute(query)
            row = result.first()

            if not row:
                return {}

            return {
                "avg_cpu_percent": float(row.avg_cpu) if row.avg_cpu else None,
                "avg_memory_percent": float(row.avg_memory) if row.avg_memory else None,
                "avg_disk_percent": float(row.avg_disk) if row.avg_disk else None,
                "total_network_bytes": (row.total_rx or 0) + (row.total_tx or 0),
                "avg_wireguard_peers": int(row.avg_wg_peers) if row.avg_wg_peers else None,
                "avg_latency_ms": float(row.avg_latency) if row.avg_latency else None,
            }

        except Exception as e:
            logger.error(f"Failed to get aggregated stats for server {server_id}: {e}")
            raise

    def get_user_key_usage(
        self,
        user_id: uuid.UUID,
        key_id: str,
    ) -> dict:
        """Get usage statistics for a user's VPN key.

        Args:
            user_id: UUID of the user
            key_id: ID of the VPN key

        Returns:
            Dictionary with usage stats
        """
        # This would need to query the agent for real-time usage
        # For now, return placeholder
        return {
            "key_id": key_id,
            "user_id": str(user_id),
            "bytes_used": 0,
            "data_limit_bytes": 0,
            "percent_used": 0.0,
        }

    @staticmethod
    def _parse_time_range(since: str) -> datetime:
        """Parse a time range string into a datetime.

        Args:
            since: Time range string (e.g., "1h", "24h", "7d", "30d")

        Returns:
            Datetime representing the start of the range

        Raises:
            ValueError: If the time range format is invalid
        """
        now = datetime.now()

        if since.endswith("h"):
            try:
                hours = int(since[:-1])
                return now - timedelta(hours=hours)
            except ValueError:
                raise ValueError(f"Invalid time range: {since}")
        elif since.endswith("d"):
            try:
                days = int(since[:-1])
                return now - timedelta(days=days)
            except ValueError:
                raise ValueError(f"Invalid time range: {since}")
        else:
            raise ValueError(f"Invalid time range format: {since}. Use '1h', '24h', '7d', or '30d'")

    def get_latest_wireguard_metrics(
        self,
        server_id: uuid.UUID,
    ) -> dict | None:
        """Get the latest WireGuard metrics for a server.

        Args:
            server_id: UUID of the server

        Returns:
            Dictionary with latest WireGuard metrics, or None if not found
        """
        try:
            query = (
                select(WireGuardMetricModel)
                .where(WireGuardMetricModel.server_id == str(server_id))
                .order_by(desc(WireGuardMetricModel.timestamp))
                .limit(1)
            )

            result = self.session.execute(query)
            metric = result.scalar_one_or_none()

            if not metric:
                return None

            return metric.to_dict()

        except Exception as e:
            logger.error(f"Failed to get latest WireGuard metric for server {server_id}: {e}")
            raise

    def get_wireguard_metrics_by_range(
        self,
        server_id: uuid.UUID,
        since: str = "24h",
    ) -> list[dict]:
        """Get WireGuard metrics for a server within a time range.

        Args:
            server_id: UUID of the server
            since: Time range string (e.g., "1h", "24h", "7d", "30d")

        Returns:
            List of metric dictionaries
        """
        try:
            from_date = self._parse_time_range(since)

            query = (
                select(WireGuardMetricModel)
                .where(WireGuardMetricModel.server_id == str(server_id))
                .where(WireGuardMetricModel.timestamp >= from_date)
                .order_by(desc(WireGuardMetricModel.timestamp))
                .limit(500)
            )

            result = self.session.execute(query)
            metrics = result.scalars().all()

            return [m.to_dict() for m in metrics]

        except Exception as e:
            logger.error(f"Failed to get WireGuard metrics for server {server_id}: {e}")
            raise

    def cleanup_old_metrics(self, retention_days: int = 30) -> dict:
        """Clean up old metrics beyond retention period.

        Args:
            retention_days: Number of days to retain metrics (default: 30)

        Returns:
            Dictionary with counts of deleted metrics
        """
        try:
            from sqlalchemy import delete

            cutoff = datetime.now(UTC) - timedelta(days=retention_days)

            # Delete old WireGuard metrics
            wg_result = self.session.execute(
                delete(WireGuardMetricModel).where(WireGuardMetricModel.timestamp < cutoff)
            )

            # Delete old Server metrics
            server_result = self.session.execute(
                delete(ServerMetricModel).where(ServerMetricModel.timestamp < cutoff)
            )

            self.session.commit()

            return {
                "wireguard_metrics_deleted": int(wg_result.rowcount or 0),  # type: ignore[attr-defined]
                "server_metrics_deleted": int(server_result.rowcount or 0),  # type: ignore[attr-defined]
                "cutoff": cutoff.isoformat(),
                "retention_days": retention_days,
            }

        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            self.session.rollback()
            raise
