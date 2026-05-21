"""Key cleanup job - Cleans up inactive keys and resets billing cycles."""

import logging
from datetime import UTC, datetime, timedelta

from usipipo_commons.domain.enums.key_status import KeyStatus

from src.core.application.services.vpn_infrastructure_service import (
    VpnInfrastructureService,
)
from src.core.domain.interfaces.i_vpn_key_repository import IVpnKeyRepository

logger = logging.getLogger(__name__)

# Constants
INACTIVE_DAYS_THRESHOLD = 90  # Keys inactive for 90+ days are cleaned up
BILLING_CYCLE_DAYS = 30  # Billing cycle is 30 days


async def cleanup_inactive_keys(
    key_repo: IVpnKeyRepository,
    vpn_infra_service: VpnInfrastructureService,
) -> dict:
    """
    Desactiva claves que han estado inactivas por más de 90 días.

    Args:
        key_repo: Repositorio de claves VPN
        vpn_infra_service: Servicio de infraestructura VPN

    Returns:
        Dict con {"deactivated": int, "errors": list}
    """
    try:
        all_keys = key_repo.get_all_active()
        now = datetime.now(UTC)
        threshold = now - timedelta(days=INACTIVE_DAYS_THRESHOLD)

        deactivated = 0
        errors = []

        for key in all_keys:
            # Verificar si la clave ha estado inactiva
            if key.last_seen_at and key.last_seen_at < threshold:
                try:
                    # Deshabilitar en el servidor VPN
                    result = vpn_infra_service.disable_key(key.id, key.key_type)

                    if result.get("success"):
                        # Update status directly on the existing key
                        key.status = KeyStatus.EXPIRED
                        key_repo.update(key)
                        deactivated += 1
                        logger.info(f"Deactivated inactive key {key.id} (user: {key.user_id})")
                    else:
                        error_msg = result.get("error", "Unknown error")
                        errors.append(f"Key {key.id}: {error_msg}")
                        logger.warning(f"Failed to deactivate key {key.id}: {error_msg}")

                except Exception as e:
                    errors.append(f"Key {key.id}: {str(e)}")
                    logger.error(f"Error deactivating key {key.id}: {e}")

        return {"deactivated": deactivated, "errors": errors}

    except Exception as e:
        logger.error(f"Error in cleanup_inactive_keys: {e}")
        return {"deactivated": 0, "errors": [str(e)]}


async def reset_data_usage(
    key_repo: IVpnKeyRepository,
    vpn_infra_service: VpnInfrastructureService,
) -> dict:
    """
    Resetea el uso de datos para claves que completaron su ciclo de billing.

    Args:
        key_repo: Repositorio de claves VPN
        vpn_infra_service: Servicio de infraestructura VPN

    Returns:
        Dict con {"reset": int, "errors": list}
    """
    try:
        keys_needing_reset = key_repo.get_keys_needing_reset()
        now = datetime.now(UTC)

        reset_count = 0
        errors = []

        for key in keys_needing_reset:
            try:
                # Verificar si realmente necesita reset (billing_reset_at < now - 30 days)
                if key.billing_reset_at and key.billing_reset_at < now - timedelta(
                    days=BILLING_CYCLE_DAYS
                ):
                    # Resetear uso de datos directly on the existing key
                    key.used_bytes = 0
                    key.billing_reset_at = now
                    key_repo.update(key)
                    reset_count += 1
                    logger.info(f"Reset data usage for key {key.id} (user: {key.user_id})")

            except Exception as e:
                errors.append(f"Key {key.id}: {str(e)}")
                logger.error(f"Error resetting usage for key {key.id}: {e}")

        return {"reset": reset_count, "errors": errors}

    except Exception as e:
        logger.error(f"Error in reset_data_usage: {e}")
        return {"reset": 0, "errors": [str(e)]}


async def check_and_notify_data_limits(
    key_repo: IVpnKeyRepository,
    vpn_infra_service: VpnInfrastructureService,
) -> dict:
    """
    Verifica claves que excedieron su límite de datos y las deshabilita.

    Args:
        key_repo: Repositorio de claves VPN
        vpn_infra_service: Servicio de infraestructura VPN

    Returns:
        Dict con {"blocked": int, "errors": list}
    """
    try:
        all_keys = key_repo.get_all_active()

        blocked = 0
        errors = []

        for key in all_keys:
            # Verificar si excedió el límite
            if key.used_gb >= key.data_limit_gb:
                try:
                    # Deshabilitar en el servidor VPN
                    result = vpn_infra_service.disable_key(key.id, key.key_type)

                    if result.get("success"):
                        blocked += 1
                        logger.info(
                            f"Blocked key {key.id} (user: {key.user_id}) - "
                            f"Exceeded limit: {key.used_gb:.2f}/{key.data_limit_gb:.2f} GB"
                        )
                        # TODO: Enviar notificación al usuario
                    else:
                        error_msg = result.get("error", "Unknown error")
                        errors.append(f"Key {key.id}: {error_msg}")
                        logger.warning(
                            f"Failed to block key {key.id} for exceeding limit: {error_msg}"
                        )

                except Exception as e:
                    errors.append(f"Key {key.id}: {str(e)}")
                    logger.error(f"Error blocking key {key.id} for exceeding limit: {e}")

        return {"blocked": blocked, "errors": errors}

    except Exception as e:
        logger.error(f"Error in check_and_notify_data_limits: {e}")
        return {"blocked": 0, "errors": [str(e)]}


async def key_cleanup_job(
    key_repo: IVpnKeyRepository,
    vpn_infra_service: VpnInfrastructureService,
) -> dict:
    """
    Job principal de limpieza de claves.
    Ejecuta todas las tareas de limpieza:
    1. Desactivar claves inactivas (90+ días)
    2. Resetear uso de datos (ciclo de 30 días)
    3. Bloquear claves que excedieron límite

    Args:
        key_repo: Repositorio de claves VPN
        vpn_infra_service: Servicio de infraestructura VPN

    Returns:
        Dict con resultados de todas las tareas
    """
    logger.info("Starting key cleanup job...")

    results = {
        "timestamp": datetime.now(UTC).isoformat(),
        "cleanup_inactive": await cleanup_inactive_keys(key_repo, vpn_infra_service),
        "reset_usage": await reset_data_usage(key_repo, vpn_infra_service),
        "block_exceeded": await check_and_notify_data_limits(key_repo, vpn_infra_service),
    }

    logger.info(f"Key cleanup job completed: {results}")
    return results
