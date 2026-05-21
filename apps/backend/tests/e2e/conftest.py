"""
Pytest fixtures for E2E tests.

Provides:
- Test database (SQLite for speed)
- Mocked HTTP client for agent API
- Authenticated test users (JWT tokens)
- Clean state between tests
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
import respx
from httpx import ASGITransport, AsyncClient
from respx import MockRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from usipipo_commons.domain.entities.user import User

from src.infrastructure.persistence.database import Base
from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel
from src.main import app
from src.shared.config import settings

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionMaker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def test_database() -> AsyncGenerator[None]:
    """Create test database tables and clean up after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def client(test_database: None) -> AsyncGenerator[AsyncClient]:
    """Create test HTTP client with mocked transport."""
    # Override the app's database dependency to use test database
    from src.infrastructure.persistence import database as db_module

    async def override_get_db():
        async with TestSessionMaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[db_module.get_db] = override_get_db

    # Disable rate limiting
    original_rate_limit = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = False

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
        settings.RATE_LIMIT_ENABLED = original_rate_limit


@pytest.fixture(scope="function")
def mocked_agent_api() -> MockRouter:
    """Mock agent API responses."""
    with respx.mock as mock:
        mock.get("http://test-agent/health").mock(
            return_value=respx.models.Response(
                status_code=200,
                json={
                    "status": "healthy",
                    "agent_status": "online",
                    "wireguard": {"status": "ok"},
                    "timestamp": 1234567890,
                },
            )
        )

        mock.post("http://test-agent/wireguard/peers").mock(
            return_value=respx.models.Response(
                status_code=201,
                json={
                    "public_key": "wg-pubkey-123",
                    "config": "[Peer]\nPublicKey = wg-pubkey-123\n...",
                    "ip_address": "10.0.0.2",
                },
            )
        )

        mock.delete("http://test-agent/wireguard/peers/wg-pubkey-123").mock(
            return_value=respx.models.Response(status_code=204)
        )

        yield mock


@pytest.fixture
async def test_user(test_database: None) -> User:
    """Create test user."""
    user = User(
        id=uuid.uuid4(),
        telegram_id=123456789,
        username="testuser",
        email="test@example.com",
        is_active=True,
    )

    async with TestSessionMaker() as session:
        user_model = UserModel(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )
        session.add(user_model)
        await session.commit()

    return user


@pytest.fixture
async def test_vpn_server(test_database: None) -> VpnServerModel:
    """Create test VPN server."""
    server = VpnServerModel(
        id=uuid.uuid4(),
        name="Test Server US",
        agent_url="http://test-agent",
        _agent_api_key="agent_test123",
        location="US",
        is_active=True,
        server_type="both",
    )

    async with TestSessionMaker() as session:
        session.add(server)
        await session.commit()

    return server


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate auth headers for test user."""
    return {
        "Authorization": f"Bearer test-token-{test_user.id}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="function")
async def clean_database(test_database: None) -> None:
    """Clean database between tests."""
    async with TestSessionMaker() as session:
        await session.execute(text("DELETE FROM vpn_keys"))
        await session.execute(text("DELETE FROM vpn_servers"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
