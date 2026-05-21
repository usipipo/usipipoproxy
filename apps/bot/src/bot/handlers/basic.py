"""Handlers para comandos básicos del bot."""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.main import BasicMessages
from src.infrastructure.logger import get_logger

logger = get_logger("handlers.basic")


class BasicHandler:
    """Handler para comandos básicos."""

    def __init__(self):
        logger.info("BasicHandler initialized")

    async def start_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Muestra el mensaje de bienvenida."""
        if update.message is None:
            logger.warning("start_handler called with no message")
            return
        user = update.effective_user
        logger.info(f"User {user.id if user else 'unknown'} started the bot")
        await update.message.reply_text(text=BasicMessages.START_TEXT)

    async def help_handler(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Muestra la lista de comandos disponibles y opción de soporte."""
        if update.message is None:
            logger.warning("help_handler called with no message")
            return
        user = update.effective_user
        logger.info(f"User {user.id if user else 'unknown'} requested help")

        # Send help message with support info
        await update.message.reply_text(
            text=BasicMessages.HELP_TEXT,
            parse_mode="Markdown",
        )

        # Send support help message
        await update.message.reply_text(
            text=BasicMessages.SUPPORT_HELP,
            parse_mode="Markdown",
        )
