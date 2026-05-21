"""Tests for referral schemas."""

import uuid

import pytest
from pydantic import ValidationError

from src.shared.schemas.referral import (
    ReferralApplyOnRegisterRequest,
    ReferralApplyOnRegisterResponse,
)


class TestReferralApplyOnRegisterRequest:
    """Tests for ReferralApplyOnRegisterRequest schema."""

    def test_valid_request(self):
        """Valid request with user_id and referral_code."""
        user_id = uuid.uuid4()
        request = ReferralApplyOnRegisterRequest(
            user_id=user_id,
            referral_code="ref_abc123def456",
        )
        assert request.user_id == user_id
        assert request.referral_code == "ref_abc123def456"

    def test_missing_user_id_fails(self):
        """Request without user_id should fail validation."""
        with pytest.raises(ValidationError):
            ReferralApplyOnRegisterRequest(referral_code="ref_abc123")

    def test_missing_referral_code_fails(self):
        """Request without referral_code should fail validation."""
        with pytest.raises(ValidationError):
            ReferralApplyOnRegisterRequest(user_id=uuid.uuid4())

    def test_empty_referral_code_fails(self):
        """Empty referral_code should fail validation."""
        with pytest.raises(ValidationError):
            ReferralApplyOnRegisterRequest(user_id=uuid.uuid4(), referral_code="")


class TestReferralApplyOnRegisterResponse:
    """Tests for ReferralApplyOnRegisterResponse schema."""

    def test_success_response(self):
        """Valid success response."""
        response = ReferralApplyOnRegisterResponse(
            success=True,
            message="Referral applied successfully",
            referral_code="ref_abc123",
            credits_earned=50,
        )
        assert response.success is True
        assert response.credits_earned == 50

    def test_error_response(self):
        """Error response without referral_code."""
        response = ReferralApplyOnRegisterResponse(
            success=False,
            message="Already have a referrer",
            referral_code=None,
            credits_earned=0,
        )
        assert response.success is False
        assert response.referral_code is None
