"""Routes para gestión de dispositivos."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from usipipo_commons.schemas.user import UserResponse

from src.infrastructure.api.v1.deps import get_current_user, get_db
from src.infrastructure.persistence.repositories.device_repository import DeviceRepository
from src.shared.schemas.device import (
    DeviceListResponse,
    DeviceRegisterRequest,
    DeviceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["Devices"])


def _get_device_repo(db: Session) -> DeviceRepository:
    """Obtiene repositorio de dispositivos."""
    return DeviceRepository(db)


@router.post(
    "/register",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    request: DeviceRegisterRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registra un nuevo dispositivo para el usuario autenticado.

    Permite registrar dispositivos para recibir notificaciones push.
    Un usuario puede tener múltiples dispositivos registrados.

    Args:
        request: Datos del dispositivo
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        DeviceResponse: Dispositivo registrado

    Raises:
        HTTPException: 400 si el platform es inválido
    """
    repo = _get_device_repo(db)

    # Check if device with same push_token already exists
    if request.push_token:
        existing_devices = repo.get_by_user_id(current_user.id)
        for device in existing_devices:
            if device.push_token == request.push_token:
                # Update existing device
                repo.update_last_active(device.id)
                logger.info(f"Device updated for user {current_user.id}")
                return DeviceResponse.model_validate(device)

    # Create new device
    device = repo.create(
        user_id=current_user.id,
        platform=request.platform,
        push_token=request.push_token,
        app_version=request.app_version,
        device_name=request.device_name,
    )

    logger.info(f"Device registered for user {current_user.id}: {device.platform}")
    return DeviceResponse.model_validate(device)


@router.get(
    "",
    response_model=DeviceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_user_devices(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = False,
):
    """
    Obtiene todos los dispositivos del usuario autenticado.

    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        active_only: Si True, solo devuelve dispositivos activos

    Returns:
        DeviceListResponse: Lista de dispositivos
    """
    repo = _get_device_repo(db)

    if active_only:
        devices = repo.get_active_by_user_id(current_user.id)
    else:
        devices = repo.get_by_user_id(current_user.id)

    return DeviceListResponse(
        devices=[DeviceResponse.model_validate(d) for d in devices],
        total=len(devices),
    )


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_200_OK,
)
def delete_device(
    device_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Elimina un dispositivo del usuario autenticado.

    Args:
        device_id: UUID del dispositivo
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        dict: Mensaje de confirmación

    Raises:
        HTTPException: 404 si el dispositivo no existe o no pertenece al usuario
    """
    repo = _get_device_repo(db)

    # Get device
    device = repo.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Verify ownership
    if str(device.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device does not belong to user",
        )

    # Delete device
    success = repo.delete(device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete device",
        )

    logger.info(f"Device deleted for user {current_user.id}: {device_id}")
    return {"message": "Device deleted successfully"}


@router.post(
    "/{device_id}/deactivate",
    status_code=status.HTTP_200_OK,
)
def deactivate_device(
    device_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desactiva un dispositivo (sin eliminarlo).

    Útil para dispositivos temporales que se pueden reactivar después.

    Args:
        device_id: UUID del dispositivo
        current_user: Usuario autenticado
        db: Sesión de base de datos

    Returns:
        dict: Mensaje de confirmación

    Raises:
        HTTPException: 404 si el dispositivo no existe o no pertenece al usuario
    """
    repo = _get_device_repo(db)

    # Get device
    device = repo.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    # Verify ownership
    if str(device.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device does not belong to user",
        )

    # Deactivate device
    success = repo.deactivate(device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate device",
        )

    logger.info(f"Device deactivated for user {current_user.id}: {device_id}")
    return {"message": "Device deactivated successfully"}
