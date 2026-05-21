import uuid
from typing import Protocol

from usipipo_commons.domain.entities import DataPackage


class IDataPackageRepository(Protocol):
    """
    Contrato para la persistencia de paquetes de datos.
    Define cómo interactuamos con la tabla de paquetes en la BD.
    """

    def save(self, data_package: DataPackage, current_user_id: uuid.UUID) -> DataPackage:
        """Guarda un nuevo paquete de datos o actualiza uno existente."""
        ...

    def get_by_id(
        self, package_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> DataPackage | None:
        """Busca un paquete específico por su ID."""
        ...

    def get_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[DataPackage]:
        """Recupera todos los paquetes de un usuario."""
        ...

    def get_active_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[DataPackage]:
        """Recupera solo los paquetes activos de un usuario."""
        ...

    def get_valid_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> list[DataPackage]:
        """Recupera los paquetes activos y no expirados de un usuario."""
        ...

    def update_usage(
        self, package_id: uuid.UUID, bytes_used: int, current_user_id: uuid.UUID
    ) -> bool:
        """Actualiza el uso de datos de un paquete."""
        ...

    def deactivate(self, package_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Desactiva un paquete."""
        ...

    def delete(self, package_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """Elimina un paquete de la base de datos."""
        ...

    def get_expired_packages(self, current_user_id: uuid.UUID) -> list[DataPackage]:
        """Recupera todos los paquetes activos que han expirado."""
        ...

    def get_by_telegram_payment_id(
        self, telegram_payment_id: str, current_user_id: uuid.UUID
    ) -> DataPackage | None:
        """Busca un paquete por el ID de pago de Telegram."""
        ...

    def get_by_user_paginated(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        offset: int = 0,
        current_user_id: uuid.UUID | None = None,
    ) -> list[DataPackage]:
        """Get packages for a user with pagination."""
        ...

    def count_by_user(
        self, user_id: uuid.UUID, current_user_id: uuid.UUID | None = None
    ) -> int:
        """Count total packages for a user."""
        ...
