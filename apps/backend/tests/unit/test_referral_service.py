"""Tests unitarios para ReferralService."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from usipipo_commons.domain.entities.user import User

from src.core.application.services.referral_service import ReferralService


@pytest.fixture
def mock_referral_repo():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def referral_service(mock_user_repo, mock_referral_repo):
    return ReferralService(mock_user_repo, mock_referral_repo)


@pytest.mark.asyncio
async def test_register_referral_success(referral_service, mock_user_repo, mock_referral_repo):
    """Test registro de referido exitoso."""
    referrer_id = uuid.uuid4()
    new_user_id = uuid.uuid4()

    referrer = User(
        id=referrer_id,
        telegram_id=1,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    new_user = User(
        id=new_user_id,
        telegram_id=2,
        username="new",
        first_name="N",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="NEW456",
        referred_by=None,
    )

    # Mocks
    mock_user_repo.get_by_referral_code.return_value = referrer
    mock_user_repo.get_by_id.return_value = new_user
    mock_referral_repo.save.return_value = AsyncMock()

    result = await referral_service.register_referral(new_user_id, "REF123")

    assert result["success"] is True
    assert result["referrer_id"] == referrer_id

    # Verificar que se actualizaron los usuarios (referente y nuevo usuario)
    assert new_user.referred_by == referrer_id
    assert mock_user_repo.update.call_count == 2


@pytest.mark.asyncio
async def test_redeem_credits_for_data_success(referral_service, mock_user_repo):
    """Test canje de creditos por datos."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        telegram_id=1,
        username="u",
        first_name="U",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="U",
        referred_by=None,
        referral_credits=200,
    )

    mock_user_repo.get_by_id.return_value = user

    # Canjear 100 creditos (suponiendo que settings.REFERRAL_CREDITS_PER_GB = 100)
    result = await referral_service.redeem_credits_for_data(user_id, 100)

    assert result["success"] is True
    assert result["gb_added"] == 1
    assert user.balance_gb == 6.0
    assert user.referral_credits == 100
    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_register_referral_by_user_id_success(
    referral_service, mock_user_repo, mock_referral_repo
):
    """Test registro de referido usando user_id UUID."""
    referrer_id = uuid.uuid4()
    new_user_id = uuid.uuid4()

    referrer = User(
        id=referrer_id,
        telegram_id=1,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    new_user = User(
        id=new_user_id,
        telegram_id=2,
        username="new",
        first_name="N",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="NEW456",
        referred_by=None,
    )

    mock_user_repo.get_by_referral_code.return_value = referrer
    mock_user_repo.get_by_id.return_value = new_user
    mock_referral_repo.save.return_value = AsyncMock()

    result = await referral_service.register_referral_by_user_id(
        user_id=new_user_id, referral_code="REF123"
    )

    assert result["success"] is True
    assert result["referrer_id"] == referrer_id
    assert new_user.referred_by == referrer_id


@pytest.mark.asyncio
async def test_register_referral_by_user_id_user_not_found(referral_service, mock_user_repo):
    """Test registro de referido cuando usuario no existe por user_id."""
    referrer = User(
        id=uuid.uuid4(),
        telegram_id=1,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )

    mock_user_repo.get_by_referral_code.return_value = referrer
    mock_user_repo.get_by_id.return_value = None

    result = await referral_service.register_referral_by_user_id(
        user_id=uuid.uuid4(), referral_code="REF123"
    )

    assert result["success"] is False
    assert result["error"] == "user_not_found"


@pytest.mark.asyncio
async def test_register_referral_by_user_id_invalid_code(referral_service, mock_user_repo):
    """Test registro de referido con codigo invalido."""
    mock_user_repo.get_by_referral_code.return_value = None
    mock_user_repo.get_by_id.return_value = AsyncMock()

    result = await referral_service.register_referral_by_user_id(
        user_id=uuid.uuid4(), referral_code="INVALID"
    )

    assert result["success"] is False
    assert result["error"] == "invalid_code"


@pytest.mark.asyncio
async def test_register_referral_by_user_id_self_referral(referral_service, mock_user_repo):
    """Test auto-referencia (mismo usuario)."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        telegram_id=1,
        username="self",
        first_name="S",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )

    mock_user_repo.get_by_referral_code.return_value = user
    mock_user_repo.get_by_id.return_value = user

    result = await referral_service.register_referral_by_user_id(
        user_id=user_id, referral_code="REF123"
    )

    assert result["success"] is False
    assert result["error"] == "self_referral"


@pytest.mark.asyncio
async def test_register_referral_by_user_id_already_referred(referral_service, mock_user_repo):
    """Test registro de referido cuando usuario ya tiene referente."""
    referrer_id = uuid.uuid4()
    new_user_id = uuid.uuid4()

    referrer = User(
        id=referrer_id,
        telegram_id=1,
        username="ref",
        first_name="R",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="REF123",
        referred_by=None,
    )
    new_user = User(
        id=new_user_id,
        telegram_id=2,
        username="new",
        first_name="N",
        last_name="",
        is_admin=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        balance_gb=5.0,
        total_purchased_gb=0.0,
        referral_code="NEW456",
        referred_by=uuid.uuid4(),  # Ya tiene referente
    )

    mock_user_repo.get_by_referral_code.return_value = referrer
    mock_user_repo.get_by_id.return_value = new_user

    result = await referral_service.register_referral_by_user_id(
        user_id=new_user_id, referral_code="REF123"
    )

    assert result["success"] is False
    assert result["error"] == "already_referred"
