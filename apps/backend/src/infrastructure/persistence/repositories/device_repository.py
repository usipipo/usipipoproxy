"""Repositorio de dispositivos con SQLAlchemy."""

import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.infrastructure.persistence.database import get_execute_rowcount
from src.infrastructure.persistence.models.device_model import DeviceModel


class DeviceRepository:
    """Implementación de repositorio de dispositivos con SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, device_id: uuid.UUID) -> DeviceModel | None:
        """
        Obtiene dispositivo por ID.

        Args:
            device_id: UUID del dispositivo

        Returns:
            DeviceModel o None si no existe
        """
        result = self.session.execute(select(DeviceModel).where(DeviceModel.id == device_id))
        return result.scalar_one_or_none()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[DeviceModel]:
        """
        Obtiene todos los dispositivos de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de dispositivos
        """
        result = self.session.execute(
            select(DeviceModel)
            .where(DeviceModel.user_id == user_id)
            .order_by(DeviceModel.created_at.desc())
        )
        return list(result.scalars().all())

    def get_active_by_user_id(self, user_id: uuid.UUID) -> list[DeviceModel]:
        """
        Obtiene dispositivos activos de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Lista de dispositivos activos
        """
        result = self.session.execute(
            select(DeviceModel)
            .where(DeviceModel.user_id == user_id, DeviceModel.is_active)
            .order_by(DeviceModel.created_at.desc())
        )
        return list(result.scalars().all())

    def create(
        self,
        user_id: uuid.UUID,
        platform: str,
        push_token: str | None = None,
        app_version: str | None = None,
        device_name: str | None = None,
    ) -> DeviceModel:
        """
        Crea un nuevo dispositivo.

        Args:
            user_id: UUID del usuario
            platform: Plataforma (android, ios, windows, linux, telegram)
            push_token: Token para push notifications
            app_version: Versión de la aplicación
            device_name: Nombre del dispositivo

        Returns:
            DeviceModel creado
        """
        device = DeviceModel(
            user_id=user_id,
            platform=platform,
            push_token=push_token,
            app_version=app_version,
            device_name=device_name,
        )
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def update_last_active(self, device_id: uuid.UUID) -> bool:
        """
        Actualiza last_active_at del dispositivo.

        Args:
            device_id: UUID del dispositivo

        Returns:
            True si se actualizó, False si no existe
        """
        result = self.session.execute(
            update(DeviceModel)
            .where(DeviceModel.id == device_id)
            .values(last_active_at=datetime.utcnow())
        )
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def deactivate(self, device_id: uuid.UUID) -> bool:
        """
        Desactiva un dispositivo.

        Args:
            device_id: UUID del dispositivo

        Returns:
            True si se desactivó, False si no existe
        """
        result = self.session.execute(
            update(DeviceModel).where(DeviceModel.id == device_id).values(is_active=False)
        )
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def delete(self, device_id: uuid.UUID) -> bool:
        """
        Elimina un dispositivo.

        Args:
            device_id: UUID del dispositivo

        Returns:
            True si se eliminó, False si no existe
        """
        result = self.session.execute(delete(DeviceModel).where(DeviceModel.id == device_id))
        self.session.commit()
        return get_execute_rowcount(result) > 0

    def delete_by_user_id(self, user_id: uuid.UUID) -> int:
        """
        Elimina todos los dispositivos de un usuario.

        Args:
            user_id: UUID del usuario

        Returns:
            Cantidad de dispositivos eliminados
        """
        result = self.session.execute(
            delete(DeviceModel).where(DeviceModel.user_id == user_id)
        )
        self.session.commit()
        return get_execute_rowcount(result)
