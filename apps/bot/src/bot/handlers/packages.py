"""Handlers para gestión de paquetes de datos (Data Packages)."""

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, PreCheckoutQueryHandler

from src.bot.keyboards.packages import PackagesKeyboard
from src.bot.keyboards.messages_packages import PackagesMessages
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PackagesHandler:
    """Handler para gestión de paquetes de datos y pagos."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("PackagesHandler initialized")

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

    async def show_packages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de paquetes de datos."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"User {telegram_id} viewing packages menu")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        PackagesMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get available packages from backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/data-packages", headers=headers)
                packages = response if isinstance(response, list) else []
            except Exception:
                # Fallback to default packages if endpoint not available
                packages = [
                    {
                        "id": "basic",
                        "name": "Básico",
                        "data_gb": 10,
                        "price_usd": 2.08,
                        "price_stars": 250,
                    },
                    {
                        "id": "standard",
                        "name": "Estándar",
                        "data_gb": 30,
                        "price_usd": 5.00,
                        "price_stars": 600,
                    },
                    {
                        "id": "advanced",
                        "name": "Avanzado",
                        "data_gb": 60,
                        "price_usd": 8.00,
                        "price_stars": 960,
                    },
                    {
                        "id": "premium",
                        "name": "Premium",
                        "data_gb": 120,
                        "price_usd": 12.00,
                        "price_stars": 1440,
                    },
                    {
                        "id": "unlimited",
                        "name": "Ilimitado",
                        "data_gb": 200,
                        "price_usd": 15.00,
                        "price_stars": 1800,
                    },
                ]

            if not packages:
                message = PackagesMessages.Menu.NO_PACKAGES
                keyboard = PackagesKeyboard.back_to_menu()
            else:
                message = PackagesMessages.Menu.PACKAGES_LIST
                for pkg in packages:
                    message += PackagesMessages.Menu.PACKAGE_ITEM.format(
                        name=pkg.get("name", "Unknown"),
                        data=f"{pkg.get('data_gb', 0):.0f}",
                        price_usd=f"{pkg.get('price_usd', 0):.2f}",
                        price_stars=pkg.get("price_stars", 0),
                    )

                keyboard = PackagesKeyboard.packages_menu(packages)

            if update.callback_query:
                await self._safe_edit_message(update.callback_query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing packages menu: {e}")
            if update.callback_query:
                await self._safe_edit_message(
                    update.callback_query,
                    context,
                    PackagesMessages.Error.SYSTEM_ERROR,
                    PackagesKeyboard.back_to_menu(),
                )
            elif update.message:
                await update.message.reply_text(
                    PackagesMessages.Error.SYSTEM_ERROR,
                    reply_markup=PackagesKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def select_package(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra detalles de un paquete y opciones de pago."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract package_id from callback_data
        package_id = query.data.replace("select_package_", "")
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} selecting package: {package_id}")

        try:
            # Get package details
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/data-packages", headers=headers)
                packages: list = response if isinstance(response, list) else []
                package = next((p for p in packages if p.get("id") == package_id), None)
            except Exception:
                # Fallback
                package = None

            if not package:
                # Fallback to default packages
                default_packages = {
                    "basic": {
                        "name": "Básico",
                        "data_gb": 10,
                        "price_usd": 2.08,
                        "price_stars": 250,
                    },
                    "standard": {
                        "name": "Estándar",
                        "data_gb": 30,
                        "price_usd": 5.00,
                        "price_stars": 600,
                    },
                    "advanced": {
                        "name": "Avanzado",
                        "data_gb": 60,
                        "price_usd": 8.00,
                        "price_stars": 960,
                    },
                    "premium": {
                        "name": "Premium",
                        "data_gb": 120,
                        "price_usd": 12.00,
                        "price_stars": 1440,
                    },
                    "unlimited": {
                        "name": "Ilimitado",
                        "data_gb": 200,
                        "price_usd": 15.00,
                        "price_stars": 1800,
                    },
                }
                package = default_packages.get(package_id)

            if not package:
                message = PackagesMessages.Error.INVALID_PACKAGE
                keyboard = PackagesKeyboard.back_to_menu()
            else:
                # Store selected package in user_data
                if context.user_data is not None:
                    context.user_data["selected_package"] = package

                message = PackagesMessages.Menu.PACKAGE_DETAILS.format(
                    name=package.get("name", "Unknown"),
                    data=f"{package.get('data_gb', 0):.0f}",
                    price_usd=f"{package.get('price_usd', 0):.2f}",
                    price_stars=package.get("price_stars", 0),
                )
                keyboard = PackagesKeyboard.payment_method_selection(package_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error selecting package: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def select_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra opciones de método de pago para un paquete."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract package_id from callback_data
        parts = query.data.split("_")
        package_id = parts[-1] if len(parts) > 1 else "basic"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} selecting payment method for package: {package_id}")

        try:
            # Get package from context or fetch again
            package = None
            if context.user_data is not None:
                package = context.user_data.get("selected_package")

            if not package:
                headers = await self._get_auth_headers(telegram_id)
                try:
                    response = await self.api.get("/data-packages", headers=headers)
                    packages: list = response if isinstance(response, list) else []
                    package = next((p for p in packages if p.get("id") == package_id), None)
                except Exception:
                    package = None

            if not package:
                message = PackagesMessages.Error.INVALID_PACKAGE
                keyboard = PackagesKeyboard.back_to_menu()
            else:
                message = PackagesMessages.Payment.SELECT_METHOD.format(
                    name=package.get("name", "Unknown"),
                    data=f"{package.get('data_gb', 0):.0f}",
                    price_usd=f"{package.get('price_usd', 0):.2f}",
                    price_stars=package.get("price_stars", 0),
                )
                keyboard = PackagesKeyboard.payment_method_selection(package_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error selecting payment method: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def pay_with_stars(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de pago con Telegram Stars."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract package_id from callback_data
        parts = query.data.split("_")
        package_id = parts[-1] if len(parts) > 1 else "basic"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} paying with stars for package: {package_id}")

        try:
            # Get package details
            package = None
            if context.user_data is not None:
                package = context.user_data.get("selected_package")

            if not package:
                headers = await self._get_auth_headers(telegram_id)
                try:
                    response = await self.api.get("/data-packages", headers=headers)
                    packages: list = response if isinstance(response, list) else []
                    package = next((p for p in packages if p.get("id") == package_id), None)
                except Exception:
                    package = None

            if not package:
                message = PackagesMessages.Error.INVALID_PACKAGE
                keyboard = PackagesKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            # Store package for later use
            if context.user_data is not None:
                context.user_data["selected_package"] = package

            # Create Stars payment via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                payment_response = await self.api.post(
                    "/payments/stars",
                    headers=headers,
                    data={
                        "package_id": package_id,
                        "telegram_id": telegram_id,
                    },
                )
                payment_id = payment_response.get("payment_id")
                stars_amount = payment_response.get("stars_amount", package.get("price_stars", 0))
                title = payment_response.get("title", f"Paquete {package.get('name', 'Unknown')}")
                description = payment_response.get(
                    "description",
                    f"{package.get('data_gb', 0):.0f} GB de datos VPN",
                )

            except Exception as e:
                logger.error(f"Error creating stars payment: {e}")
                # Fallback to direct Telegram invoice
                payment_id = f"stars_{package_id}_{telegram_id}"
                stars_amount = package.get("price_stars", 600)
                title = f"Paquete {package.get('name', 'Unknown')}"
                description = f"{package.get('data_gb', 0):.0f} GB de datos VPN"

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
                    start_parameter=f"stars_{package_id}",
                    need_name=False,
                    need_email=False,
                    need_shipping_address=False,
                    send_phone_number_to_provider=False,
                    send_email_to_provider=False,
                    is_flexible=False,
                )

                message = PackagesMessages.Payment.STARS_PAYMENT_SENT.format(
                    stars=stars_amount,
                )
                keyboard = PackagesKeyboard.back_to_packages()
                await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error processing stars payment: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
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
            # Extract package info from payload
            # Payload format: stars_{package_id}_{telegram_id}
            parts = payment_payload.split("_")
            package_id = parts[1] if len(parts) > 2 else "basic"

            # Get package details
            package = None
            if context.user_data is not None:
                package = context.user_data.get("selected_package")

            if not package:
                headers = await self._get_auth_headers(telegram_id)
                try:
                    response = await self.api.get("/data-packages", headers=headers)
                    packages: list = response if isinstance(response, list) else []
                    package = next((p for p in packages if p.get("id") == package_id), None)
                except Exception:
                    package = None

            # Activate package via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                activation_response = await self.api.post(
                    "/payments/stars/activate",
                    headers=headers,
                    data={
                        "payment_id": payment_payload,
                        "package_id": package_id,
                        "telegram_payment_id": successful_payment.telegram_payment_charge_id,
                    },
                )
                success = activation_response.get("success", False)
                error_message = activation_response.get("error_message")

            except Exception as e:
                logger.error(f"Error activating package: {e}")
                success = False
                error_message = str(e)

            if success:
                message = PackagesMessages.Payment.STARS_SUCCESS.format(
                    data=f"{package.get('data_gb', 0):.0f}" if package else "N/A",
                    name=package.get("name", "Paquete") if package else "Paquete",
                )
                keyboard = PackagesKeyboard.back_to_menu()
                logger.info(f"User {telegram_id} successfully activated package {package_id}")
            else:
                message = PackagesMessages.Payment.STARS_FAILED.format(
                    reason=error_message or "Error desconocido",
                )
                keyboard = PackagesKeyboard.back_to_menu()
                logger.warning(f"User {telegram_id} failed to activate package: {error_message}")

            await update.message.reply_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            # Clear selected package from context
            if context.user_data is not None and "selected_package" in context.user_data:
                del context.user_data["selected_package"]

        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            if update.message:
                await update.message.reply_text(
                    text=PackagesMessages.Error.SYSTEM_ERROR,
                    reply_markup=PackagesKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def pay_with_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de pago con criptomonedas (USDT)."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract package_id from callback_data
        parts = query.data.split("_")
        package_id = parts[-1] if len(parts) > 1 else "basic"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} paying with crypto for package: {package_id}")

        try:
            # Get package details
            package = None
            if context.user_data is not None:
                package = context.user_data.get("selected_package")

            if not package:
                headers = await self._get_auth_headers(telegram_id)
                try:
                    response = await self.api.get("/data-packages", headers=headers)
                    packages: list = response if isinstance(response, list) else []
                    package = next((p for p in packages if p.get("id") == package_id), None)
                except Exception:
                    package = None

            if not package:
                message = PackagesMessages.Error.INVALID_PACKAGE
                keyboard = PackagesKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            # Store package for later use
            if context.user_data is not None:
                context.user_data["selected_package"] = package

            # Create crypto payment via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                payment_response = await self.api.post(
                    "/payments/crypto",
                    headers=headers,
                    data={
                        "package_id": package_id,
                        "telegram_id": telegram_id,
                        "currency": "USDT",
                    },
                )
                payment_id = payment_response.get("payment_id")
                payment_address = payment_response.get("payment_address")
                amount_usd = payment_response.get("amount_usd", package.get("price_usd", 0))
                network = payment_response.get("network", "TRC20")

            except Exception as e:
                logger.error(f"Error creating crypto payment: {e}")
                message = PackagesMessages.Error.CRYPTO_PAYMENT_FAILED
                keyboard = PackagesKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            if not payment_id:
                logger.error("No payment_id in response")
                message = PackagesMessages.Error.CRYPTO_PAYMENT_FAILED
                keyboard = PackagesKeyboard.back_to_menu()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            # Show payment instructions
            message = PackagesMessages.Payment.CRYPTO_PAYMENT.format(
                amount=f"{amount_usd:.2f}",
                network=network,
                address=payment_address,
                package_name=package.get("name", "Unknown"),
                data_gb=f"{package.get('data_gb', 0):.0f}",
            )
            keyboard = PackagesKeyboard.crypto_payment_status(payment_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error processing crypto payment: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
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

            except Exception:
                status = "pending"
                amount_usd = 0

            if status == "completed":
                message = PackagesMessages.Payment.CRYPTO_SUCCESS
                keyboard = PackagesKeyboard.back_to_menu()
            elif status == "expired":
                message = PackagesMessages.Payment.CRYPTO_EXPIRED
                keyboard = PackagesKeyboard.back_to_packages()
            else:
                message = PackagesMessages.Payment.CRYPTO_PENDING.format(
                    amount=f"{amount_usd:.2f}",
                )
                keyboard = PackagesKeyboard.crypto_payment_status(payment_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error checking crypto payment status: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def view_data_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el resumen de uso de datos del usuario."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing data summary")

        try:
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/users/me/data-summary", headers=headers)

                total_data_gb = response.get("total_data_gb", 0)
                used_data_gb = response.get("used_data_gb", 0)
                remaining_data_gb = response.get("remaining_data_gb", 0)
                active_packages = response.get("active_packages", 0)
                next_renewal = response.get("next_renewal")

            except Exception:
                # Fallback if endpoint not available
                total_data_gb = 0
                used_data_gb = 0
                remaining_data_gb = 0
                active_packages = 0
                next_renewal = None

            usage_percentage = (used_data_gb / total_data_gb * 100) if total_data_gb > 0 else 0

            if active_packages == 0:
                message = PackagesMessages.Summary.NO_ACTIVE_PACKAGES
                keyboard = PackagesKeyboard.packages_menu_button()
            else:
                message = PackagesMessages.Summary.DATA_SUMMARY.format(
                    total=f"{total_data_gb:.1f}",
                    used=f"{used_data_gb:.1f}",
                    remaining=f"{remaining_data_gb:.1f}",
                    percentage=f"{usage_percentage:.0f}",
                    packages=active_packages,
                    renewal=next_renewal[:10] if next_renewal else "N/A",
                )
                keyboard = PackagesKeyboard.data_summary_menu()

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing data summary: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def show_slots_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de gestión de slots de datos."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing slots menu")

        try:
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/users/me/slots", headers=headers)
                slots: list = response if isinstance(response, list) else []
                max_slots = response.get("max_slots", 5) if isinstance(response, dict) else 5
                used_slots = (
                    len([s for s in slots if s.get("status") == "active"])
                    if isinstance(response, list)
                    else 0
                )

            except Exception:
                # Fallback if endpoint not available
                slots = []
                max_slots = 5
                used_slots = 0

            if not slots:
                message = PackagesMessages.Slots.NO_SLOTS
                keyboard = PackagesKeyboard.slots_menu(has_packages=False)
            else:
                message = PackagesMessages.Slots.SLOTS_HEADER.format(
                    used=used_slots,
                    max=max_slots,
                )

                for slot in slots:
                    status_icon = "🟢" if slot.get("status") == "active" else "🔴"
                    package_name = slot.get("package_name", "Paquete")
                    data_gb = slot.get("data_gb", 0)
                    expires = slot.get("expires_at", "N/A")

                    message += PackagesMessages.Slots.SLOT_ITEM.format(
                        status=status_icon,
                        name=package_name,
                        data=f"{data_gb:.0f}",
                        expires=expires[:10] if expires else "N/A",
                    )

                keyboard = PackagesKeyboard.slots_menu(has_packages=len(slots) < max_slots)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing slots menu: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def buy_extra_slot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo para comprar un slot extra de datos."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} buying extra slot")

        try:
            headers = await self._get_auth_headers(telegram_id)

            # Check if user can buy more slots
            try:
                response = await self.api.get("/users/me/slots", headers=headers)
                slots = response if isinstance(response, list) else []
                max_slots = response.get("max_slots", 5) if isinstance(response, dict) else 5
                used_slots = (
                    len([s for s in slots if s.get("status") == "active"])
                    if isinstance(response, list)
                    else 0
                )

            except Exception:
                used_slots = 0
                max_slots = 5

            if used_slots >= max_slots:
                message = PackagesMessages.Slots.MAX_SLOTS_REACHED.format(max=max_slots)
                keyboard = PackagesKeyboard.back_to_menu()
            else:
                message = PackagesMessages.Slots.BUY_SLOT_PROMPT
                keyboard = PackagesKeyboard.buy_slot_confirmation()

                # Store state for next step
                if context.user_data is not None:
                    context.user_data["buying_slot"] = True

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error buying extra slot: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def confirm_buy_slot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirma la compra de un slot extra."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} confirming extra slot purchase")

        try:
            # Clear state
            if context.user_data is not None and "buying_slot" in context.user_data:
                del context.user_data["buying_slot"]

            # Buy slot via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.post(
                    "/users/me/slots",
                    headers=headers,
                    data={},
                )
                success = response.get("success", False)
                slot_id = response.get("slot_id")

            except Exception as e:
                logger.error(f"Error buying slot: {e}")
                success = False
                slot_id = None

            if success:
                message = PackagesMessages.Slots.SLOT_PURCHASED
                keyboard = PackagesKeyboard.slots_menu(has_packages=True)
                logger.info(f"User {telegram_id} successfully bought extra slot {slot_id}")
            else:
                message = PackagesMessages.Slots.SLOT_PURCHASE_FAILED
                keyboard = PackagesKeyboard.back_to_menu()
                logger.warning(f"User {telegram_id} failed to buy extra slot")

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error confirming slot purchase: {e}")
            await self._safe_edit_message(
                query,
                context,
                PackagesMessages.Error.SYSTEM_ERROR,
                PackagesKeyboard.back_to_menu(),
            )

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú principal."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)

        from src.bot.keyboards.main_menu import MainMenuKeyboard
        from src.bot.keyboards.main import BasicMessages

        # Show main menu with buttons
        message = BasicMessages.BACK_TO_MAIN
        keyboard = MainMenuKeyboard.main_menu()

        await self._safe_edit_message(query, context, message, keyboard, parse_mode="Markdown")


def get_packages_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de comandos para paquetes de datos."""
    handler = PackagesHandler(api_client, token_storage)

    return [
        CommandHandler("comprar", handler.show_packages),
        CommandHandler("packages", handler.show_packages),
        CommandHandler("paquetes", handler.show_packages),
    ]


def get_packages_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de callbacks para paquetes de datos."""
    handler = PackagesHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_packages, pattern="^buy_gb_menu$"),
        CallbackQueryHandler(handler.select_package, pattern="^select_package_"),
        CallbackQueryHandler(handler.select_payment_method, pattern="^select_payment_"),
        CallbackQueryHandler(handler.pay_with_stars, pattern="^pay_stars_"),
        CallbackQueryHandler(handler.pay_with_crypto, pattern="^pay_crypto_"),
        CallbackQueryHandler(handler.view_data_summary, pattern="^view_data_summary$"),
        CallbackQueryHandler(handler.show_slots_menu, pattern="^buy_slots_menu$"),
        CallbackQueryHandler(handler.buy_extra_slot, pattern="^buy_extra_slot$"),
        CallbackQueryHandler(handler.confirm_buy_slot, pattern="^confirm_buy_slot$"),
        CallbackQueryHandler(handler.check_crypto_payment_status, pattern="^check_crypto_status_"),
        CallbackQueryHandler(handler.back_to_main_menu, pattern="^packages_back_to_main$"),
    ]


def get_packages_payment_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de pago para paquetes de datos."""
    handler = PackagesHandler(api_client, token_storage)

    return [
        PreCheckoutQueryHandler(handler.pre_checkout_callback),
    ]
