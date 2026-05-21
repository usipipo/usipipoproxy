"""Handler global para menú principal."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.main_menu import MainMenuKeyboard
from src.bot.keyboards.main import BasicMessages

logger = logging.getLogger(__name__)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja callback 'main_menu' - muestra menú principal con botones.

    Args:
        update: Update de Telegram
        context: Contexto del bot
    """
    query = update.callback_query
    if query is None:
        logger.warning("show_main_menu called without callback_query")
        return

    await query.answer()

    logger.info(f"User {query.from_user.id} navigating to main menu")

    try:
        await query.edit_message_text(
            text=BasicMessages.BACK_TO_MAIN,
            reply_markup=MainMenuKeyboard.main_menu(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error showing main menu: {e}")
        await query.edit_message_text(
            text="❌ Error al mostrar el menú principal. Intenta de nuevo.",
        )
