"""Tests for Referrals Keyboards."""

import pytest
from telegram import InlineKeyboardMarkup


class TestReferralsKeyboards:
    """Tests for ReferralsKeyboard class."""

    @pytest.mark.asyncio
    async def test_menu_keyboard_exists_and_has_buttons(self):
        """menu() keyboard exists and has buttons."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        keyboard = ReferralsKeyboard.menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

        # Check for referral_redeem button
        buttons = keyboard.inline_keyboard
        assert any("referral_redeem" in btn.callback_data for row in buttons for btn in row)

        # Check for referral_apply button
        assert any("referral_apply" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_menu_keyboard_with_referral_link_has_share_button(self):
        """menu() with referral_link includes share button as first row."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        referral_link = "https://t.me/usipipobot?start=abc123"
        keyboard = ReferralsKeyboard.menu(referral_link=referral_link)

        assert isinstance(keyboard, InlineKeyboardMarkup)

        # Should have 3 rows: share, redeem, apply
        assert len(keyboard.inline_keyboard) == 3

        # First row should be share button with switch_inline_query
        share_button = keyboard.inline_keyboard[0][0]
        assert share_button.text == "📤 Compartir Enlace"
        assert share_button.switch_inline_query == referral_link
        assert share_button.callback_data is None

    @pytest.mark.asyncio
    async def test_menu_keyboard_without_referral_link_has_no_share_button(self):
        """menu() without referral_link has no share button."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        keyboard = ReferralsKeyboard.menu()

        # Should have 2 rows: redeem, apply (no share)
        assert len(keyboard.inline_keyboard) == 2

        # No button with URL should exist
        for row in keyboard.inline_keyboard:
            for btn in row:
                assert btn.url is None

    @pytest.mark.asyncio
    async def test_redeem_confirmation_keyboard_exists(self):
        """redeem_confirmation() keyboard exists."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        keyboard = ReferralsKeyboard.redeem_confirmation(credits=100)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

        # Check for confirm button with credits
        buttons = keyboard.inline_keyboard
        assert any(
            "referral_redeem_confirm:100" in btn.callback_data for row in buttons for btn in row
        )

        # Check for cancel button
        assert any("referral_cancel" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_apply_code_keyboard_exists(self):
        """apply_code() keyboard exists."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        keyboard = ReferralsKeyboard.apply_code()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

        # Check for back button
        buttons = keyboard.inline_keyboard
        assert any("referral_back" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_back_to_menu_keyboard_exists(self):
        """back_to_menu() keyboard exists."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        keyboard = ReferralsKeyboard.back_to_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

        # Check for back button
        buttons = keyboard.inline_keyboard
        assert any("referral_back" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_callback_data_patterns_are_correct(self):
        """Callback data patterns are correct."""
        from src.bot.keyboards.referrals import ReferralsKeyboard

        # Test menu callback patterns
        menu_keyboard = ReferralsKeyboard.menu()
        menu_buttons = menu_keyboard.inline_keyboard
        menu_callbacks = [btn.callback_data for row in menu_buttons for btn in row]

        assert "referral_redeem" in menu_callbacks
        assert "referral_apply" in menu_callbacks

        # Test redeem_confirmation callback patterns
        confirm_keyboard = ReferralsKeyboard.redeem_confirmation(credits=50)
        confirm_buttons = confirm_keyboard.inline_keyboard
        confirm_callbacks = [btn.callback_data for row in confirm_buttons for btn in row]

        assert "referral_redeem_confirm:50" in confirm_callbacks
        assert "referral_cancel" in confirm_callbacks

        # Test apply_code callback patterns
        apply_keyboard = ReferralsKeyboard.apply_code()
        apply_buttons = apply_keyboard.inline_keyboard
        apply_callbacks = [btn.callback_data for row in apply_buttons for btn in row]

        assert "referral_back" in apply_callbacks

        # Test back_to_menu callback patterns
        back_keyboard = ReferralsKeyboard.back_to_menu()
        back_buttons = back_keyboard.inline_keyboard
        back_callbacks = [btn.callback_data for row in back_buttons for btn in row]

        assert "referral_back" in back_callbacks
