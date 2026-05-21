"""Entry point for running the Telegram bot."""

import os

from src.infrastructure.logger import get_logger

logger = get_logger("main")


def main() -> None:
    """Main entry point."""
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        logger.error("TELEGRAM_TOKEN not configured. Check .env file.")
        raise RuntimeError("TELEGRAM_TOKEN not configured")

    from src.main import create_application

    application = create_application(token)
    logger.info("Bot application created successfully")

    try:
        logger.info("Starting bot with polling...")
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
