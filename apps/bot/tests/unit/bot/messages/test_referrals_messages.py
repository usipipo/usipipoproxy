"""Tests for Referrals Messages."""

import pytest


class TestReferralsMessages:
    """Tests for ReferralsMessages class."""

    @pytest.mark.asyncio
    async def test_menu_category_exists(self):
        """ReferralsMessages.Menu category exists."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert hasattr(ReferralsMessages, "Menu")

    @pytest.mark.asyncio
    async def test_error_category_exists(self):
        """ReferralsMessages.Error category exists."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert hasattr(ReferralsMessages, "Error")

    @pytest.mark.asyncio
    async def test_referral_stats_has_correct_placeholders(self):
        """REFERRAL_STATS has correct placeholders."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert "{referral_code}" in ReferralsMessages.Menu.REFERRAL_STATS
        assert "{total_referrals}" in ReferralsMessages.Menu.REFERRAL_STATS
        assert "{referral_credits}" in ReferralsMessages.Menu.REFERRAL_STATS
        assert "{referral_link}" in ReferralsMessages.Menu.REFERRAL_STATS

    @pytest.mark.asyncio
    async def test_invite_link_has_correct_placeholders(self):
        """INVITE_LINK has correct placeholders."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert "{referral_link}" in ReferralsMessages.Menu.INVITE_LINK

    @pytest.mark.asyncio
    async def test_redeem_confirmation_exists(self):
        """REDEEM_CONFIRMATION message exists."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert hasattr(ReferralsMessages.Menu, "REDEEM_CONFIRMATION")
        assert ReferralsMessages.Menu.REDEEM_CONFIRMATION is not None

    @pytest.mark.asyncio
    async def test_all_error_messages_exist(self):
        """All error messages exist."""
        from src.bot.keyboards.messages_referrals import ReferralsMessages

        assert hasattr(ReferralsMessages.Error, "NOT_AUTHENTICATED")
        assert hasattr(ReferralsMessages.Error, "INVALID_CODE")
        assert hasattr(ReferralsMessages.Error, "SELF_REFERRAL")
        assert hasattr(ReferralsMessages.Error, "ALREADY_REFERRED")
        assert hasattr(ReferralsMessages.Error, "INSUFFICIENT_CREDITS")
        assert hasattr(ReferralsMessages.Error, "SYSTEM_ERROR")
