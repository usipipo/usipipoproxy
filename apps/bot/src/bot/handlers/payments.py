"""Handlers para gestión de pagos y suscripciones (Payments & Subscriptions)."""

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from src.bot.keyboards.messages_payments import PaymentsMessages
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PaymentsHandler:
    """Handler para gestión de pagos y suscripciones."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("PaymentsHandler initialized")

    async def _get_auth_headers(self, telegram_id: int) -> dict[str, str]:
        """Obtiene headers de autenticación para el usuario."""
        tokens = await self.tokens.get(telegram_id)
        if not tokens:
            raise PermissionError("User not authenticated")
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    async def _safe_answer_query(self, query: Any) -> None:
        """Responde a callback query de forma segura."""
        try:
            await query.answer()
        except Exception as e:
            logger.error(f"Error answering query: {e}")

    async def _safe_edit_message(
        self,
        query: Any,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup: Any = None,
        parse_mode: str = "Markdown",
    ) -> None:
        """Edita mensaje de forma segura."""
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")

    async def show_payment_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de pagos."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"User {telegram_id} viewing payment menu")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        PaymentsMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get payment methods from backend (optional)
            headers = await self._get_auth_headers(telegram_id)
            payment_methods: list = []
            try:
                # Try to get available payment methods
                response = await self.api.get("/payments/methods", headers=headers)
                payment_methods = response if isinstance(response, list) else []
            except Exception:
                # Fallback to default payment methods
                payment_methods = [
                    {"id": "crypto", "name": "Criptomonedas (USDT)", "enabled": True},
                    {"id": "stars", "name": "Telegram Stars", "enabled": True},
                ]

            if not payment_methods:
                message = PaymentsMessages.Menu.NO_PAYMENT_METHODS
                keyboard = PaymentsKeyboard.back_to_menu()
            else:
                message = PaymentsMessages.Menu.PAYMENT_METHODS
                keyboard = PaymentsKeyboard.payment_menu(payment_methods)

            if update.callback_query:
                await self._safe_edit_message(update.callback_query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing payment menu: {e}")
            if update.callback_query:
                await self._safe_edit_message(
                    update.callback_query,
                    context,
                    PaymentsMessages.Error.SYSTEM_ERROR,
                    PaymentsKeyboard.back_to_menu(),
                )
            elif update.message:
                await update.message.reply_text(
                    PaymentsMessages.Error.SYSTEM_ERROR,
                    reply_markup=PaymentsKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def pay_with_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de pago con criptomonedas (USDT - TronDealer)."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract amount from callback_data
        parts = query.data.split("_")
        amount = parts[-1] if len(parts) > 1 else "10"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} paying with crypto, amount: {amount}")

        try:
            # Create crypto payment via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                payment_response = await self.api.post(
                    "/payments/crypto",
                    headers=headers,
                    data={
                        "amount_usd": float(amount),
                        "telegram_id": telegram_id,
                        "currency": "USDT",
                    },
                )
                payment_id = payment_response.get("payment_id")
                payment_address = payment_response.get("payment_address")
                amount_usd = payment_response.get("amount_usd", float(amount))
                network = payment_response.get("network", "TRC20")
                qr_code_url = payment_response.get("qr_code_url")

            except Exception as e:
                logger.error(f"Error creating crypto payment: {e}")
                message = PaymentsMessages.Error.CRYPTO_PAYMENT_FAILED
                keyboard = PaymentsKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            if not payment_id:
                logger.error("No payment_id in response")
                message = PaymentsMessages.Error.CRYPTO_PAYMENT_FAILED
                keyboard = PaymentsKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            # Show payment instructions
            message = PaymentsMessages.Payment.CRYPTO_PAYMENT.format(
                amount=f"{amount_usd:.2f}",
                network=network,
                address=payment_address,
                qr_url=qr_code_url or "",
            )
            keyboard = PaymentsKeyboard.crypto_payment_status(payment_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error processing crypto payment: {e}")
            await self._safe_edit_message(
                query,
                context,
                PaymentsMessages.Error.SYSTEM_ERROR,
                PaymentsKeyboard.back_to_menu(),
            )

    async def pay_with_stars(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de pago con Telegram Stars."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract amount from callback_data
        parts = query.data.split("_")
        amount = parts[-1] if len(parts) > 1 else "600"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} paying with stars, amount: {amount}")

        try:
            # Create Stars payment via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                payment_response = await self.api.post(
                    "/payments/stars",
                    headers=headers,
                    data={
                        "stars_amount": int(amount),
                        "telegram_id": telegram_id,
                    },
                )
                payment_id = payment_response.get("payment_id")
                stars_amount = payment_response.get("stars_amount", int(amount))
                title = payment_response.get("title", "Recarga de Saldo")
                description = payment_response.get(
                    "description",
                    f"Recarga de {stars_amount} Stars para servicios VPN",
                )

            except Exception as e:
                logger.error(f"Error creating stars payment: {e}")
                # Fallback to direct Telegram invoice
                payment_id = f"stars_{amount}_{telegram_id}"
                stars_amount = int(amount)
                title = "Recarga de Saldo"
                description = f"Recarga de {stars_amount} Stars para servicios VPN"

            # Send invoice via Telegram Bot API
            if update.effective_chat and payment_id and stars_amount:
                from telegram import LabeledPrice

                await context.bot.send_invoice(
                    chat_id=update.effective_chat.id,
                    title=title,
                    description=description,
                    payload=payment_id,
                    provider_token="",  # Empty for Telegram Stars
                    currency="XTR",  # Telegram Stars currency
                    prices=[LabeledPrice(label=title, amount=stars_amount)],
                    start_parameter=f"stars_{amount}",
                    need_name=False,
                    need_email=False,
                    need_shipping_address=False,
                    send_phone_number_to_provider=False,
                    send_email_to_provider=False,
                    is_flexible=False,
                )

                message = PaymentsMessages.Payment.STARS_PAYMENT_SENT.format(
                    stars=stars_amount,
                )
                keyboard = PaymentsKeyboard.back_to_payments()
                await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error processing stars payment: {e}")
            await self._safe_edit_message(
                query,
                context,
                PaymentsMessages.Error.SYSTEM_ERROR,
                PaymentsKeyboard.back_to_menu(),
            )

    async def view_payment_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el historial de pagos del usuario."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing payment history")

        try:
            headers = await self._get_auth_headers(telegram_id)

            # Extract page from callback data if present
            page = 0
            if query.data and "_" in query.data:
                try:
                    page = int(query.data.split("_")[-1])
                except ValueError:
                    page = 0

            # Get payment history from backend
            try:
                response = await self.api.get(
                    f"/payments/history?page={page}&limit=10",
                    headers=headers,
                )
                payments = response.get("payments", [])
                total = response.get("total", 0)
                crypto_count = response.get("crypto_count", 0)
                stars_count = response.get("stars_count", 0)
                completed_count = response.get("completed_count", 0)
                pending_count = response.get("pending_count", 0)
                has_more = response.get("has_more", False)
            except Exception:
                # Endpoint may not be implemented yet
                payments = []
                total = 0
                crypto_count = 0
                stars_count = 0
                completed_count = 0
                pending_count = 0
                has_more = False

            if not payments:
                message = PaymentsMessages.History.NO_PAYMENTS
                keyboard = PaymentsKeyboard.back_to_menu()
            else:
                message = PaymentsMessages.History.HEADER.format(
                    total=total,
                    crypto=crypto_count,
                    stars=stars_count,
                    completed=completed_count,
                    pending=pending_count,
                )

                for payment in payments:
                    status_icon = (
                        "⏳"
                        if payment.get("status") == "pending"
                        else "✅"
                        if payment.get("status") == "completed"
                        else "❌"
                        if payment.get("status") == "failed"
                        else "⚪"
                    )

                    payment_type = (
                        "🪙 Crypto"
                        if payment.get("type") == "crypto"
                        else "⭐ Stars"
                        if payment.get("type") == "stars"
                        else "💳"
                    )

                    message += PaymentsMessages.History.PAYMENT_ITEM.format(
                        date=payment.get("created_at", "N/A")[:10],
                        type=payment_type,
                        amount=f"{payment.get('amount_usd', 0):.2f}"
                        if payment.get("type") == "crypto"
                        else f"{payment.get('stars_amount', 0)} ⭐",
                        status=status_icon,
                        status_text=payment.get("status", "unknown").upper(),
                    )

                keyboard = PaymentsKeyboard.payment_history_list(
                    has_next=has_more,
                    page=page,
                )

            if update.callback_query:
                await self._safe_edit_message(query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error viewing payment history: {e}")
            await self._safe_edit_message(
                query,
                context,
                PaymentsMessages.Error.SYSTEM_ERROR,
                PaymentsKeyboard.back_to_menu(),
            )

    async def pre_checkout_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el callback de pre-checkout de Telegram."""
        pre_checkout_query = update.pre_checkout_query
        if pre_checkout_query is None:
            return

        logger.info(f"Pre-checkout query from user {pre_checkout_query.from_user.id}")

        try:
            # Validate payment
            # In production, you should validate the invoice here
            await pre_checkout_query.answer(ok=True)
            logger.info("Pre-checkout approved")

        except Exception as e:
            logger.error(f"Error in pre-checkout: {e}")
            if pre_checkout_query:
                await pre_checkout_query.answer(ok=False, error_message="Error en el pago")

    async def successful_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el pago exitoso de Telegram Stars."""
        if update.message is None or update.message.successful_payment is None:
            return

        successful_payment = update.message.successful_payment
        telegram_id = update.effective_user.id if update.effective_user else 0
        payment_payload = successful_payment.invoice_payload

        logger.info(f"User {telegram_id} successful payment: {payment_payload}")

        try:
            # Extract payment info from payload
            # Payload format: stars_{amount}_{telegram_id} or custom payment_id
            parts = payment_payload.split("_")
            amount = parts[1] if len(parts) > 1 else "0"

            # Activate payment via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                activation_response = await self.api.post(
                    "/payments/stars/activate",
                    headers=headers,
                    data={
                        "payment_id": payment_payload,
                        "telegram_payment_id": successful_payment.telegram_payment_charge_id,
                        "stars_amount": int(amount) if amount.isdigit() else 0,
                    },
                )
                success = activation_response.get("success", False)
                error_message = activation_response.get("error_message")
                credited_amount = activation_response.get("credited_amount", 0)

            except Exception as e:
                logger.error(f"Error activating payment: {e}")
                success = False
                error_message = str(e)
                credited_amount = 0

            if success:
                message = PaymentsMessages.Payment.STARS_SUCCESS.format(
                    stars=credited_amount if credited_amount > 0 else amount,
                )
                keyboard = PaymentsKeyboard.back_to_menu()
                logger.info(
                    f"User {telegram_id} successfully activated stars payment: {payment_payload}"
                )
            else:
                message = PaymentsMessages.Payment.STARS_FAILED.format(
                    reason=error_message or "Error desconocido",
                )
                keyboard = PaymentsKeyboard.back_to_menu()
                logger.warning(
                    f"User {telegram_id} failed to activate stars payment: {error_message}"
                )

            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            if update.message:
                await update.message.reply_text(
                    text=PaymentsMessages.Error.SYSTEM_ERROR,
                    reply_markup=PaymentsKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def check_crypto_payment_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verifica el estado de un pago con criptomonedas."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract payment_id from callback_data
        parts = query.data.split("_")
        payment_id = parts[-1] if len(parts) > 1 else ""
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} checking crypto payment status: {payment_id}")

        try:
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get(
                    f"/payments/crypto/{payment_id}/status",
                    headers=headers,
                )
                status = response.get("status", "pending")
                amount_usd = response.get("amount_usd", 0)
                tx_hash = response.get("transaction_hash")

            except Exception:
                status = "pending"
                amount_usd = 0
                tx_hash = None

            if status == "completed":
                message = PaymentsMessages.Payment.CRYPTO_SUCCESS
                keyboard = PaymentsKeyboard.back_to_menu()
            elif status == "expired":
                message = PaymentsMessages.Payment.CRYPTO_EXPIRED
                keyboard = PaymentsKeyboard.back_to_payments()
            else:
                message = PaymentsMessages.Payment.CRYPTO_PENDING.format(
                    amount=f"{amount_usd:.2f}",
                    tx_hash=tx_hash or "N/A",
                )
                keyboard = PaymentsKeyboard.crypto_payment_status(payment_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error checking crypto payment status: {e}")
            await self._safe_edit_message(
                query,
                context,
                PaymentsMessages.Error.SYSTEM_ERROR,
                PaymentsKeyboard.back_to_menu(),
            )


# Need to import keyboard at module level for helper functions
from src.bot.keyboards.payments import PaymentsKeyboard  # noqa: E402


def get_payments_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de comandos para pagos."""
    handler = PaymentsHandler(api_client, token_storage)

    return [
        CommandHandler("pago", handler.show_payment_menu),
        CommandHandler("pagar", handler.show_payment_menu),
        CommandHandler("historial", handler.view_payment_history),
    ]


def get_payments_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de callbacks para pagos."""
    handler = PaymentsHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_payment_menu, pattern="^payment_menu$"),
        CallbackQueryHandler(handler.pay_with_crypto, pattern="^pay_crypto_"),
        CallbackQueryHandler(handler.pay_with_stars, pattern="^pay_stars_"),
        CallbackQueryHandler(handler.view_payment_history, pattern="^payment_history"),
        CallbackQueryHandler(handler.check_crypto_payment_status, pattern="^check_crypto_status_"),
    ]


def get_payments_payment_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de pago (invoice) para pagos."""
    handler = PaymentsHandler(api_client, token_storage)

    return [
        PreCheckoutQueryHandler(handler.pre_checkout_callback),
        MessageHandler(filters.SUCCESSFUL_PAYMENT, handler.successful_payment),
    ]
