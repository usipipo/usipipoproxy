"""Tests for Server Selection Keyboards."""

import pytest
from uuid import uuid4
from telegram import InlineKeyboardMarkup


class TestServerKeyboards:
    """Tests for ServerKeyboards class."""

    @pytest.fixture
    def sample_servers(self):
        """Create sample server list for testing."""
        from usipipo_commons.domain.entities.server import Server

        return [
            Server(
                id=uuid4(),
                name="Server 1",
                country_code="US",
                country_name="United States",
                city="New York",
                max_connections=1000,
                current_connections=100,  # 10% load - low
            ),
            Server(
                id=uuid4(),
                name="Server 2",
                country_code="DE",
                country_name="Germany",
                city="Berlin",
                max_connections=1000,
                current_connections=400,  # 40% load - low
            ),
            Server(
                id=uuid4(),
                name="Server 3",
                country_code="GB",
                country_name="United Kingdom",
                city="London",
                max_connections=1000,
                current_connections=600,  # 60% load - medium
            ),
            Server(
                id=uuid4(),
                name="Server 4",
                country_code="FR",
                country_name="France",
                city="Paris",
                max_connections=1000,
                current_connections=750,  # 75% load - medium
            ),
            Server(
                id=uuid4(),
                name="Server 5",
                country_code="JP",
                country_name="Japan",
                city="Tokyo",
                max_connections=1000,
                current_connections=900,  # 90% load - high
            ),
        ]

    @pytest.fixture
    def sample_servers_many(self, sample_servers):
        """Create sample server list with more than 5 servers."""
        from usipipo_commons.domain.entities.server import Server

        additional_servers = [
            Server(
                id=uuid4(),
                name="Server 6",
                country_code="CA",
                country_name="Canada",
                city="Toronto",
                max_connections=1000,
                current_connections=200,  # 20% load - low
            ),
            Server(
                id=uuid4(),
                name="Server 7",
                country_code="AU",
                country_name="Australia",
                city="Sydney",
                max_connections=1000,
                current_connections=850,  # 85% load - high
            ),
        ]
        return sample_servers + additional_servers

    @pytest.fixture
    def sample_server_no_city(self):
        """Create a server without city."""
        from usipipo_commons.domain.entities.server import Server

        return Server(
            id=uuid4(),
            name="Server No City",
            country_code="NL",
            country_name="Netherlands",
            city=None,
            max_connections=1000,
            current_connections=300,  # 30% load - low
        )

    @pytest.fixture
    def empty_servers(self):
        """Create empty server list."""
        return []

    # ==================== server_selection() Tests ====================

    @pytest.mark.asyncio
    async def test_server_selection_returns_inline_keyboard_markup(self, sample_servers):
        """server_selection() returns InlineKeyboardMarkup."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_server_selection_shows_top_5_servers(self, sample_servers_many):
        """server_selection() shows only top 5 recommended servers."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers_many)

        # Should have 5 server buttons + 1 "show all" button + 1 back button = 7 rows
        assert len(keyboard.inline_keyboard) == 7

    @pytest.mark.asyncio
    async def test_server_selection_with_5_servers_no_show_all(self, sample_servers):
        """server_selection() with exactly 5 servers has no 'show all' button."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # Should have 5 server buttons + 1 back button = 6 rows (no "show all")
        assert len(keyboard.inline_keyboard) == 6

        # Verify no "show all" button
        buttons_text = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🔍 Ver todos los servidores" not in buttons_text

    @pytest.mark.asyncio
    async def test_server_selection_with_more_than_5_has_show_all(self, sample_servers_many):
        """server_selection() with >5 servers has 'show all' button."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers_many)

        # Verify "show all" button exists
        buttons_text = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🔍 Ver todos los servidores" in buttons_text

    @pytest.mark.asyncio
    async def test_server_selection_has_back_button(self, sample_servers):
        """server_selection() has back button."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # Verify back button exists
        buttons_text = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🔙 Volver" in buttons_text

    @pytest.mark.asyncio
    async def test_server_selection_callback_data_format(self, sample_servers):
        """server_selection() buttons have correct callback data format."""
        from src.bot.keyboards.servers import ServerKeyboards
        from uuid import UUID

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # Check server buttons have server_select:{uuid} format
        server_callbacks = [
            btn.callback_data
            for row in keyboard.inline_keyboard
            for btn in row
            if btn.callback_data and btn.callback_data.startswith("server_select:")
        ]

        assert len(server_callbacks) == 5

        # Verify format: server_select:{uuid}
        for callback in server_callbacks:
            parts = callback.split(":")
            assert len(parts) == 2
            assert parts[0] == "server_select"
            # Verify it's a valid UUID
            UUID(parts[1])

    @pytest.mark.asyncio
    async def test_server_selection_back_button_callback(self, sample_servers):
        """server_selection() back button has correct callback."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # Find back button
        back_buttons = [
            btn for row in keyboard.inline_keyboard for btn in row if btn.text == "🔙 Volver"
        ]

        assert len(back_buttons) == 1
        assert back_buttons[0].callback_data == "vpn_keys_menu"

    @pytest.mark.asyncio
    async def test_server_selection_show_all_callback(self, sample_servers_many):
        """server_selection() 'show all' button has correct callback."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers_many)

        # Find show all button
        show_all_buttons = [
            btn
            for row in keyboard.inline_keyboard
            for btn in row
            if btn.text == "🔍 Ver todos los servidores"
        ]

        assert len(show_all_buttons) == 1
        assert show_all_buttons[0].callback_data == "servers_show_all"

    # ==================== server_selection_full() Tests ====================

    @pytest.mark.asyncio
    async def test_server_selection_full_returns_inline_keyboard_markup(self, sample_servers):
        """server_selection_full() returns InlineKeyboardMarkup."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(sample_servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_server_selection_full_shows_all_servers(self, sample_servers_many):
        """server_selection_full() shows all servers."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(sample_servers_many)

        # Should have 7 server buttons + 1 back button = 8 rows
        assert len(keyboard.inline_keyboard) == 8

    @pytest.mark.asyncio
    async def test_server_selection_full_no_show_all_button(self, sample_servers_many):
        """server_selection_full() does not have 'show all' button."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(sample_servers_many)

        # Verify no "show all" button
        buttons_text = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🔍 Ver todos los servidores" not in buttons_text

    @pytest.mark.asyncio
    async def test_server_selection_full_has_back_button(self, sample_servers):
        """server_selection_full() has back button."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(sample_servers)

        # Verify back button exists
        buttons_text = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "🔙 Volver" in buttons_text

    @pytest.mark.asyncio
    async def test_server_selection_full_callback_data_format(self, sample_servers):
        """server_selection_full() buttons have correct callback data format."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(sample_servers)

        # Check server buttons have server_select:{uuid} format
        server_callbacks = [
            btn.callback_data
            for row in keyboard.inline_keyboard
            for btn in row
            if btn.callback_data and btn.callback_data.startswith("server_select:")
        ]

        assert len(server_callbacks) == 5

    # ==================== Load Emoji Tests ====================

    @pytest.mark.asyncio
    async def test_load_emoji_low_0_percent(self):
        """Load emoji is 🟢 for 0% load."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=0,  # 0% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🟢" in button_text

    @pytest.mark.asyncio
    async def test_load_emoji_low_50_percent(self):
        """Load emoji is 🟢 for 50% load (boundary)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=500,  # 50% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🟢" in button_text

    @pytest.mark.asyncio
    async def test_load_emoji_medium_51_percent(self):
        """Load emoji is 🟡 for 51% load (boundary)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=510,  # 51% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🟡" in button_text

    @pytest.mark.asyncio
    async def test_load_emoji_medium_80_percent(self):
        """Load emoji is 🟡 for 80% load (boundary)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=800,  # 80% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🟡" in button_text

    @pytest.mark.asyncio
    async def test_load_emoji_high_81_percent(self):
        """Load emoji is 🔴 for 81% load (boundary)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=810,  # 81% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🔴" in button_text

    @pytest.mark.asyncio
    async def test_load_emoji_high_100_percent(self):
        """Load emoji is 🔴 for 100% load."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=1000,
            current_connections=1000,  # 100% load
        )

        keyboard = ServerKeyboards.server_selection([server])
        button_text = keyboard.inline_keyboard[0][0].text

        assert "🔴" in button_text

    # ==================== Button Text Format Tests ====================

    @pytest.mark.asyncio
    async def test_button_text_includes_flag_and_city(self, sample_servers):
        """Button text includes country code flag and city."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # First server: US - New York
        first_button = keyboard.inline_keyboard[0][0]
        assert "US" in first_button.text
        assert "New York" in first_button.text

        # Second server: DE - Berlin
        second_button = keyboard.inline_keyboard[1][0]
        assert "DE" in second_button.text
        assert "Berlin" in second_button.text

    @pytest.mark.asyncio
    async def test_button_text_without_city(self, sample_server_no_city):
        """Button text handles null city correctly (no dash)."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection([sample_server_no_city])

        button_text = keyboard.inline_keyboard[0][0].text

        # Should be "NL 🟢" not "NL - 🟢"
        assert " - " not in button_text
        assert "NL" in button_text

    @pytest.mark.asyncio
    async def test_button_text_format_with_city(self, sample_servers):
        """Button text format is correct with city."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(sample_servers)

        # First button should be "US - New York 🟢"
        first_button = keyboard.inline_keyboard[0][0]
        assert first_button.text.startswith("US - ")
        assert "🟢" in first_button.text

    # ==================== Edge Cases ====================

    @pytest.mark.asyncio
    async def test_empty_server_list(self, empty_servers):
        """server_selection() handles empty server list."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection(empty_servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should only have back button
        assert len(keyboard.inline_keyboard) == 1
        assert keyboard.inline_keyboard[0][0].text == "🔙 Volver"

    @pytest.mark.asyncio
    async def test_empty_server_list_full_view(self, empty_servers):
        """server_selection_full() handles empty server list."""
        from src.bot.keyboards.servers import ServerKeyboards

        keyboard = ServerKeyboards.server_selection_full(empty_servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should only have back button
        assert len(keyboard.inline_keyboard) == 1
        assert keyboard.inline_keyboard[0][0].text == "🔙 Volver"

    @pytest.mark.asyncio
    async def test_server_with_zero_max_connections(self):
        """Handles server with zero max_connections (division by zero protection)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Test Server",
            country_code="US",
            country_name="United States",
            max_connections=0,  # Zero max connections
            current_connections=0,
        )

        # Should not raise division by zero error
        keyboard = ServerKeyboards.server_selection([server])

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # 1 server + 1 back button

    @pytest.mark.asyncio
    async def test_single_server(self):
        """server_selection() with single server."""
        from src.bot.keyboards.servers import ServerKeyboards
        from usipipo_commons.domain.entities.server import Server

        server = Server(
            id=uuid4(),
            name="Single Server",
            country_code="US",
            country_name="United States",
            city="New York",
            max_connections=1000,
            current_connections=100,
        )

        keyboard = ServerKeyboards.server_selection([server])

        assert len(keyboard.inline_keyboard) == 2  # 1 server + 1 back button
        assert keyboard.inline_keyboard[0][0].text == "US - New York 🟢"

    @pytest.mark.asyncio
    async def test_load_emojis_constant_exists(self):
        """LOAD_EMOJIS constant exists and has correct values."""
        from src.bot.keyboards.servers import ServerKeyboards

        assert hasattr(ServerKeyboards, "LOAD_EMOJIS")
        assert ServerKeyboards.LOAD_EMOJIS["low"] == "🟢"
        assert ServerKeyboards.LOAD_EMOJIS["medium"] == "🟡"
        assert ServerKeyboards.LOAD_EMOJIS["high"] == "🔴"
