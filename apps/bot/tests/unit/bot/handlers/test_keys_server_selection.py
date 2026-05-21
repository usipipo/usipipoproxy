"""Tests para VPN Server Selection en Keys Handlers."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestServerSelectionConversation:
    """Tests para el flujo de selección de servidor VPN."""

    @pytest.mark.asyncio
    async def test_protocol_selected_fetches_servers(self):
        """protocol_selected debe fetchear servidores del backend."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler, SELECT_SERVER

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.get.return_value = {
                "servers": [
                    {
                        "id": "srv-1",
                        "name": "US-East",
                        "country_name": "United States",
                        "city": "New York",
                        "load_level": "low",
                        "load_percentage": 25,
                    },
                    {
                        "id": "srv-2",
                        "name": "EU-West",
                        "country_name": "Germany",
                        "city": "Frankfurt",
                        "load_level": "medium",
                        "load_percentage": 65,
                    },
                ],
                "recommended": [
                    {
                        "id": "srv-1",
                        "name": "US-East",
                        "country_name": "United States",
                        "city": "New York",
                        "load_level": "low",
                        "load_percentage": 25,
                    },
                ],
            }

            handler = KeysHandler(mock_api, mock_storage)

            # Mock update and context
            mock_query = AsyncMock()
            mock_query.data = "vpn_create_outline"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {}

            result = await handler.protocol_selected(mock_update, mock_context)

            # Verify API was called
            mock_api.get.assert_called_once()
            assert "/vpn/servers?protocol=outline" in mock_api.get.call_args[0][0]

            # Verify protocol stored
            assert mock_context.user_data["vpn_protocol"] == "outline"

            # Verify state is SELECT_SERVER
            assert result == SELECT_SERVER

            # Verify message was edited
            mock_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_protocol_selected_no_servers_available(self):
        """protocol_selected maneja cuando no hay servidores."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler
            import telegram

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.get.return_value = {"servers": [], "recommended": []}

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "vpn_create_wireguard"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {}

            result = await handler.protocol_selected(mock_update, mock_context)

            # Should end conversation when no servers
            assert result == telegram.ext.ConversationHandler.END

            # Verify error message shown
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "⚠️ No hay servidores disponibles" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_protocol_selected_api_error_handling(self):
        """protocol_selected maneja errores de API."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler
            import telegram

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.get.side_effect = Exception("Connection error")

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "vpn_create_outline"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {}

            result = await handler.protocol_selected(mock_update, mock_context)

            # Should end conversation on error
            assert result == telegram.ext.ConversationHandler.END

            # Verify retry option shown
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "⚠️ Error al cargar servidores" in call_args[0][0]
            assert "reply_markup" in call_args[1]

    @pytest.mark.asyncio
    async def test_server_selected_stores_server_id(self):
        """server_selected debe guardar server_id en user_data."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler, INPUT_NAME

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "server_select:srv-123"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {"vpn_protocol": "outline"}

            result = await handler.server_selected(mock_update, mock_context)

            # Verify server_id stored
            assert mock_context.user_data["server_id"] == "srv-123"

            # Verify state is INPUT_NAME
            assert result == INPUT_NAME

            # Verify confirmation message
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "✅ Servidor seleccionado" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_server_selected_show_all_callback(self):
        """server_selected maneja callback 'servers_show_all'."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler, SELECT_SERVER

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}

            # Mock servers as dicts (API response format)
            mock_api.get.return_value = {
                "servers": [
                    {
                        "id": "srv-1",
                        "country_name": "United States",
                        "city": "New York",
                        "load_level": "low",
                    },
                    {
                        "id": "srv-2",
                        "country_name": "Germany",
                        "city": "Frankfurt",
                        "load_level": "medium",
                    },
                    {"id": "srv-3", "country_name": "Japan", "city": "Tokyo", "load_level": "high"},
                ]
            }

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "servers_show_all"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {"vpn_protocol": "outline"}

            result = await handler.server_selected(mock_update, mock_context)

            # Verify state remains SELECT_SERVER
            assert result == SELECT_SERVER

            # Verify full server list keyboard shown
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "🌍 <b>Todos los Servidores Disponibles</b>" in call_args[0][0]
            assert call_args[1]["parse_mode"] == "HTML"

    @pytest.mark.asyncio
    async def test_server_selected_show_all_api_error(self):
        """server_selected maneja errores en show_all."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler
            import telegram

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.get.side_effect = Exception("API error")

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "servers_show_all"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {"vpn_protocol": "outline"}

            result = await handler.server_selected(mock_update, mock_context)

            # Should end conversation on error
            assert result == telegram.ext.ConversationHandler.END

            # Verify error message
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "⚠️ Error al cargar servidores" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_server_selected_invalid_callback_data(self):
        """server_selected ignora callback data inválido."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler
            import telegram

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "invalid_callback"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {}

            result = await handler.server_selected(mock_update, mock_context)

            # Should end conversation for invalid data
            assert result == telegram.ext.ConversationHandler.END

    @pytest.mark.asyncio
    async def test_server_selected_missing_protocol(self):
        """server_selected maneja protocolo faltante en show_all."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler
            import telegram

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            mock_query = AsyncMock()
            mock_query.data = "servers_show_all"
            mock_update = MagicMock()
            mock_update.callback_query = mock_query
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {}  # No protocol set

            result = await handler.server_selected(mock_update, mock_context)

            # Should end conversation
            assert result == telegram.ext.ConversationHandler.END

            # Verify error message
            mock_query.edit_message_text.assert_called_once()
            call_args = mock_query.edit_message_text.call_args
            assert "⚠️ Error: Protocolo no seleccionado" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_format_server_list_message(self):
        """_format_server_list_message formatea mensaje correctamente."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            servers = [
                {
                    "id": "srv-1",
                    "name": "US-East",
                    "country_name": "United States",
                    "city": "New York",
                    "load_level": "low",
                    "load_percentage": 25,
                },
                {
                    "id": "srv-2",
                    "name": "EU-West",
                    "country_name": "Germany",
                    "city": "Frankfurt",
                    "load_level": "medium",
                    "load_percentage": 65,
                },
            ]

            message = handler._format_server_list_message(servers)

            # Verify message structure
            assert "🌍 <b>Selecciona un Servidor VPN</b>" in message
            assert "🔥 <b>Recomendados (menor carga):</b>" in message
            assert "United States" in message
            assert "New York" in message
            assert "Germany" in message
            assert "Frankfurt" in message
            assert "🟢" in message  # Low load emoji
            assert "🟡" in message  # Medium load emoji
            assert "Carga: 25%" in message
            assert "Carga: 65%" in message
            assert "ℹ️ Los servidores se actualizan en tiempo real" in message

    @pytest.mark.asyncio
    async def test_format_server_list_message_no_city(self):
        """_format_server_list_message maneja servidores sin ciudad."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            servers = [
                {
                    "id": "srv-1",
                    "name": "US-East",
                    "country_name": "United States",
                    "load_level": "low",
                    "load_percentage": 25,
                },  # No city
            ]

            message = handler._format_server_list_message(servers)

            # Should not have " - " for missing city
            assert "United States" in message
            assert " - " not in message or "United States -" not in message

    @pytest.mark.asyncio
    async def test_format_server_list_message_empty_list(self):
        """_format_server_list_message maneja lista vacía."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            message = handler._format_server_list_message([])

            # Should still have header
            assert "🌍 <b>Selecciona un Servidor VPN</b>" in message
            assert "🔥 <b>Recomendados (menor carga):</b>" in message

    @pytest.mark.asyncio
    async def test_name_received_includes_server_id(self):
        """name_received debe incluir server_id al crear clave."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.post.return_value = {
                "id": "key-123",
                "config": "wg_config_content",
                "data_limit_gb": 5.0,
            }

            handler = KeysHandler(mock_api, mock_storage)

            mock_message = AsyncMock()
            mock_message.text = "Mi Casa"
            mock_update = MagicMock()
            mock_update.message = mock_message
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {
                "vpn_protocol": "wireguard",
                "server_id": "srv-456",
            }

            await handler.name_received(mock_update, mock_context)

            # Verify API post called with server_id
            mock_api.post.assert_called_once()
            call_args = mock_api.post.call_args
            payload = call_args[1]["data"]
            assert "server_id" in payload
            assert payload["server_id"] == "srv-456"

            # Verify user_data cleared
            assert "vpn_protocol" not in mock_context.user_data
            assert "server_id" not in mock_context.user_data

    @pytest.mark.asyncio
    async def test_name_received_without_server_id(self):
        """name_received funciona sin server_id (opcional)."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token"}
            mock_api.post.return_value = {
                "id": "key-123",
                "config": "wg_config_content",
                "data_limit_gb": 5.0,
            }

            handler = KeysHandler(mock_api, mock_storage)

            mock_message = AsyncMock()
            mock_message.text = "Mi Casa"
            mock_update = MagicMock()
            mock_update.message = mock_message
            mock_update.effective_user.id = 123
            mock_context = MagicMock()
            mock_context.user_data = {
                "vpn_protocol": "outline",
                # No server_id
            }

            await handler.name_received(mock_update, mock_context)

            # Verify API post called without server_id
            mock_api.post.assert_called_once()
            call_args = mock_api.post.call_args
            payload = call_args[1]["data"]
            assert "server_id" not in payload

    @pytest.mark.asyncio
    async def test_conversation_handler_includes_select_server_state(self):
        """ConversationHandler debe incluir estado SELECT_SERVER."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import get_key_creation_conversation_handler, KeysHandler
            from telegram.ext import CallbackQueryHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            handler = KeysHandler(mock_api, mock_storage)

            conv_handler = get_key_creation_conversation_handler(handler)

            # Verify states dict has SELECT_SERVER
            assert 1 in conv_handler.states  # SELECT_SERVER = 1
            assert 2 in conv_handler.states  # INPUT_NAME = 2

            # Verify SELECT_SERVER has correct handlers
            select_server_handlers = conv_handler.states[1]
            assert len(select_server_handlers) >= 2

            # Check for server_select pattern handler
            has_server_select = any(
                isinstance(h, CallbackQueryHandler) and "server_select" in str(h.pattern)
                for h in select_server_handlers
            )
            assert has_server_select

            # Check for servers_show_all handler
            has_show_all = any(
                isinstance(h, CallbackQueryHandler) and "servers_show_all" in str(h.pattern)
                for h in select_server_handlers
            )
            assert has_show_all


class TestServerKeyboards:
    """Tests para ServerKeyboards."""

    @pytest.mark.asyncio
    async def test_server_selection_keyboard_empty_list(self):
        """server_selection maneja lista vacía de servidores."""
        from src.bot.keyboards.servers import ServerKeyboards
        from telegram import InlineKeyboardMarkup

        keyboard = ServerKeyboards.server_selection([])

        assert isinstance(keyboard, InlineKeyboardMarkup)
        buttons = keyboard.inline_keyboard

        # Should have back button
        assert any("Volver" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_server_selection_keyboard_with_servers(self):
        """server_selection crea botones con servidores (dict format)."""
        from src.bot.keyboards.servers import ServerKeyboards
        from telegram import InlineKeyboardMarkup

        servers = [
            {
                "id": "srv-1",
                "country_name": "United States",
                "country_code": "🇺🇸",
                "city": "New York",
                "load_level": "low",
            },
            {
                "id": "srv-2",
                "country_name": "Germany",
                "country_code": "🇩🇪",
                "city": "Frankfurt",
                "load_level": "medium",
            },
        ]

        keyboard = ServerKeyboards.server_selection(servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        buttons = keyboard.inline_keyboard

        # Should have server buttons
        server_buttons = [
            btn for row in buttons for btn in row if btn.callback_data.startswith("server_select:")
        ]
        assert len(server_buttons) == 2

        # Verify callback data format
        assert server_buttons[0].callback_data == "server_select:srv-1"
        assert server_buttons[1].callback_data == "server_select:srv-2"

    @pytest.mark.asyncio
    async def test_server_selection_keyboard_show_all_button(self):
        """server_selection muestra botón 'Ver todos' si hay >5 servidores."""
        from src.bot.keyboards.servers import ServerKeyboards

        servers = [
            {
                "id": f"srv-{i}",
                "country_name": f"Country {i}",
                "country_code": "🇺🇸",
                "city": f"City {i}",
                "load_level": "low",
            }
            for i in range(6)
        ]

        keyboard = ServerKeyboards.server_selection(servers)
        buttons = keyboard.inline_keyboard

        # Should have "Ver todos" button
        has_show_all = any("Ver todos" in btn.text for row in buttons for btn in row)
        assert has_show_all

    @pytest.mark.asyncio
    async def test_server_selection_keyboard_load_emojis(self):
        """server_selection asigna emojis según carga."""
        from src.bot.keyboards.servers import ServerKeyboards

        # Low load
        low_load_server = {
            "id": "srv-1",
            "country_name": "United States",
            "country_code": "🇺🇸",
            "city": "NYC",
            "load_level": "low",
        }
        # High load
        high_load_server = {
            "id": "srv-2",
            "country_name": "Germany",
            "country_code": "🇩🇪",
            "city": "FRA",
            "load_level": "high",
        }

        keyboard_low = ServerKeyboards.server_selection([low_load_server])
        keyboard_high = ServerKeyboards.server_selection([high_load_server])

        buttons_low = keyboard_low.inline_keyboard
        buttons_high = keyboard_high.inline_keyboard

        # Low load should have 🟢
        assert "🟢" in buttons_low[0][0].text

        # High load should have 🔴
        assert "🔴" in buttons_high[0][0].text

    @pytest.mark.asyncio
    async def test_server_selection_full_keyboard(self):
        """server_selection_full crea teclado con todos los servidores."""
        from src.bot.keyboards.servers import ServerKeyboards
        from telegram import InlineKeyboardMarkup

        servers = [
            {
                "id": "srv-1",
                "country_name": "United States",
                "country_code": "🇺🇸",
                "city": "New York",
                "load_level": "low",
            },
            {
                "id": "srv-2",
                "country_name": "Germany",
                "country_code": "🇩🇪",
                "city": "Frankfurt",
                "load_level": "medium",
            },
        ]

        keyboard = ServerKeyboards.server_selection_full(servers)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        buttons = keyboard.inline_keyboard

        # Should have server buttons
        server_buttons = [
            btn for row in buttons for btn in row if btn.callback_data.startswith("server_select:")
        ]
        assert len(server_buttons) == 2

        # Should have back button
        has_back = any("Volver" in btn.text for row in buttons for btn in row)
        assert has_back
