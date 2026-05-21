"""Server selection inline keyboards."""

from typing import TYPE_CHECKING

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

if TYPE_CHECKING:
    pass


class ServerKeyboards:
    """Factory for server selection inline keyboards."""

    LOAD_EMOJIS = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴",
    }

    @staticmethod
    def server_selection(servers: list) -> InlineKeyboardMarkup:
        """Create inline keyboard for server selection.

        Args:
            servers: List of servers (dicts or Server objects) sorted by load (lowest first)

        Returns:
            InlineKeyboardMarkup with server buttons
        """
        keyboard = []

        # Show top 5 recommended servers
        recommended = servers[:5]

        for server in recommended:
            # Handle both dict and object formats
            if isinstance(server, dict):
                # Dict format from API
                server_id = server.get("id")
                country_code = server.get("country_code", server.get("country_name", ""))
                city = server.get("city", "")
                load_level = server.get("load_level", "low")
            else:
                # Object format
                server_id = server.id
                country_code = getattr(server, "country_code", getattr(server, "country_name", ""))
                city = getattr(server, "city", "")
                # Calculate load level from connections
                load_pct = int((server.current_connections / max(server.max_connections, 1)) * 100)
                if load_pct <= 50:
                    load_level = "low"
                elif load_pct <= 80:
                    load_level = "medium"
                else:
                    load_level = "high"

            load_emoji = ServerKeyboards.LOAD_EMOJIS.get(load_level, "🟢")

            # Button text: Flag + Country + City + Load
            city_text = f" - {city}" if city else ""
            button_text = f"{country_code}{city_text} {load_emoji}"

            # Callback data: server_select:{server_id}
            callback_data = f"server_select:{server_id}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        # Add "Show all servers" button if more than 5 servers
        if len(servers) > 5:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🔍 Ver todos los servidores", callback_data="servers_show_all"
                    )
                ]
            )

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="vpn_keys_menu")])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def server_selection_full(servers: list) -> InlineKeyboardMarkup:
        """Create inline keyboard showing all servers.

        Args:
            servers: List of all available servers (dicts or objects)

        Returns:
            InlineKeyboardMarkup with all server buttons
        """
        keyboard = []

        for server in servers:
            # Handle both dict and object formats
            if isinstance(server, dict):
                server_id = server.get("id")
                country_code = server.get("country_code", server.get("country_name", ""))
                city = server.get("city", "")
                load_level = server.get("load_level", "low")
            else:
                server_id = server.id
                country_code = getattr(server, "country_code", getattr(server, "country_name", ""))
                city = getattr(server, "city", "")
                # Calculate load level from connections
                load_pct = int((server.current_connections / max(server.max_connections, 1)) * 100)
                if load_pct <= 50:
                    load_level = "low"
                elif load_pct <= 80:
                    load_level = "medium"
                else:
                    load_level = "high"

            load_emoji = ServerKeyboards.LOAD_EMOJIS.get(load_level, "🟢")

            city_text = f" - {city}" if city else ""
            button_text = f"{country_code}{city_text} {load_emoji}"

            callback_data = f"server_select:{server_id}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="vpn_keys_menu")])

        return InlineKeyboardMarkup(keyboard)
