"""
User factory for creating test users.
"""

import uuid

import factory

from src.core.domain.entities.user import User


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        telegram_id: int = None, username: str = None, email: str = None, is_active: bool = True
    ) -> User:
        """Create a test user."""
        return User(
            id=uuid.uuid4(),
            telegram_id=telegram_id or factory.Sequence(lambda n: 100000000 + n),
            username=username or f"testuser{factory.Sequence(lambda n: n)}",
            email=email or factory.Sequence(lambda n: f"user{n}@example.com"),
            is_active=is_active,
        )
