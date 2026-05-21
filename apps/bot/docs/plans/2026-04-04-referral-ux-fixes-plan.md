# Referral UX Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Unify referral message display across commands, fix URL rendering, and enable native Telegram sharing.

**Architecture:** Convert from Markdown to HTML parse mode for clean URL rendering, unify operations menu to reuse ReferralsMessages/ReferralsKeyboard templates, replace URL button with switch_inline_query for native Telegram share.

**Tech Stack:** Python 3.13, python-telegram-bot v21, HTML parse mode, pytest

---

### Task 1: Convert Referral Message Templates from Markdown to HTML

**Files:**
- Modify: `src/bot/keyboards/messages_referrals.py`

**Step 1: Convert REFERRAL_STATS template to HTML**

Replace Markdown syntax with HTML tags:
- `*bold*` → `<b>bold</b>`
- `` `code` `` → `<code>code</code>`
- Remove escaping needs for URLs

```python
REFERRAL_STATS = (
    "🎯 <b>Tu Programa de Referidos</b>\n\n"
    "📊 <b>Estadísticas:</b>\n"
    "• Código: <code>{referral_code}</code>\n"
    "• Total referidos: <code>{total_referrals}</code>\n"
    "• Créditos disponibles: <code>{referral_credits}</code>\n\n"
    "🔗 <b>Tu enlace:</b>\n"
    "{referral_link}\n\n"
    "💡 <b>Beneficios:</b>\n"
    "• 1 crédito por cada amigo invitado\n"
    "• 5 créditos si tu amigo compra un paquete\n\n"
    "Comparte tu enlace y gana créditos!"
)
```

**Step 2: Convert INVITE_LINK template to HTML**

```python
INVITE_LINK = (
    "🔗 <b>Tu Link de Invitación</b>\n\n"
    "{referral_link}\n\n"
    "Comparte este link con tus amigos y gana créditos cuando se unan.\n\n"
    "💰 <b>Recompensas:</b>\n"
    "• 1 crédito por cada referido\n"
    "• 10 créditos = 1 GB de datos"
)
```

**Step 3: Convert REDEEM_CONFIRMATION and APPLY_SUCCESS to HTML**

```python
REDEEM_CONFIRMATION = (
    "✅ <b>Canje Exitoso!</b>\n\n"
    "Has canjeado <code>{credits}</code> créditos por <code>{gb}</code> GB de datos.\n\n"
    "Tus créditos restantes: <code>{remaining_credits}</code>"
)

APPLY_SUCCESS = (
    "✅ <b>Código Aplicado!</b>\n\n"
    "Has aplicado el código de referido <code>{referral_code}</code>.\n"
    "¡Bienvenido al programa de referidos!"
)
```

**Step 4: Commit**

```bash
git add src/bot/keyboards/messages_referrals.py
git commit -m "refactor: convert referral templates from Markdown to HTML"
```

---

### Task 2: Update Referrals Handler to Use HTML Parse Mode

**Files:**
- Modify: `src/bot/handlers/referrals.py`
- Test: `tests/bot/test_referrals_handlers.py`

**Step 1: Remove `_escape_md()` function and all calls**

The function is no longer needed since HTML doesn't require URL escaping.

**Step 2: Change all `parse_mode="Markdown"` to `parse_mode="HTML"`**

In `show_referrals()`, `get_referral_link()`, `redeem_credits()`, `redeem_credits_callback()`, `apply_code_callback()`:
```python
parse_mode="HTML"
```

**Step 3: Remove URL escaping from referral_link**

```python
# Before:
referral_link_escaped = _escape_md(referral_link)
# After:
referral_link = f"https://t.me/usipipobot?start={referral_code}"
# Use directly, no escaping needed
```

**Step 4: Update tests to expect HTML format**

In `tests/bot/test_referrals_handlers.py`:
- Change assertions from Markdown syntax (`*bold*`) to HTML (`<b>bold</b>`)
- Remove escaped URL assertions, use plain URLs

```python
# Old:
assert "🎯 *Tu Programa de Referidos*" in call_args[1]["text"]
assert "https://t\\.me/usipipobot?start\\=ABC123" in call_args[1]["text"]
assert call_args[1]["parse_mode"] == "Markdown"

# New:
assert "🎯 <b>Tu Programa de Referidos</b>" in call_args[1]["text"]
assert "https://t.me/usipipobot?start=ABC123" in call_args[1]["text"]
assert call_args[1]["parse_mode"] == "HTML"
```

**Step 5: Run tests**

```bash
uv run pytest tests/bot/test_referrals_handlers.py -v
```
Expected: All tests pass

**Step 6: Commit**

```bash
git add src/bot/handlers/referrals.py tests/bot/test_referrals_handlers.py
git commit -m "refactor: switch referrals handler from Markdown to HTML"
```

---

### Task 3: Fix Share Button to Use switch_inline_query

**Files:**
- Modify: `src/bot/keyboards/referrals.py`

**Step 1: Change share button from URL to switch_inline_query**

```python
@staticmethod
def menu(referral_link: str | None = None) -> InlineKeyboardMarkup:
    """Main referrals menu keyboard with optional share button."""
    keyboard = []

    # Add share button as first row if referral link is provided
    if referral_link:
        share_text = "📤 Compartir Enlace"
        keyboard.append([
            InlineKeyboardButton(share_text, switch_inline_query=referral_link),
        ])

    # Add existing buttons
    keyboard.extend([
        [
            InlineKeyboardButton("💰 Canjear Créditos", callback_data="referral_redeem"),
        ],
        [
            InlineKeyboardButton("📝 Aplicar Código", callback_data="referral_apply"),
        ],
    ])

    return InlineKeyboardMarkup(keyboard)
```

**Step 2: Commit**

```bash
git add src/bot/keyboards/referrals.py
git commit -m "feat: use switch_inline_query for referral share button"
```

---

### Task 4: Unify Operations Menu Referral Display

**Files:**
- Modify: `src/bot/handlers/operations.py`
- Modify: `src/bot/keyboards/messages_operations.py` (optional cleanup)

**Step 1: Import ReferralsMessages and ReferralsKeyboard**

```python
from src.bot.keyboards.messages_referrals import ReferralsMessages
from src.bot.keyboards.referrals import ReferralsKeyboard
```

**Step 2: Rewrite show_referrals to use unified template**

```python
async def show_referrals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de referidos."""
    query = update.callback_query
    if query is None or update.effective_user is None:
        return

    await self._safe_answer_query(query)
    telegram_id = update.effective_user.id

    logger.info(f"👥 User {telegram_id} viewing referrals")

    try:
        # Get referral stats from backend
        invited = 0
        credits = 0
        referral_code = str(telegram_id)

        try:
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get("/referrals/me", headers=headers)
            invited = response.get("total_referrals", 0)
            credits = response.get("referral_credits", 0)
            referral_code = response.get("referral_code", referral_code)
        except Exception:
            pass

        # Build referral link
        link = f"https://t.me/usipipobot?start={referral_code}"

        # Use unified template
        message = ReferralsMessages.Menu.REFERRAL_STATS.format(
            referral_code=referral_code,
            total_referrals=invited,
            referral_credits=credits,
            referral_link=link,
        )
        keyboard = ReferralsKeyboard.menu(link)

        await self._safe_edit_message(query, context, message, keyboard, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error en show_referrals: {e}")
        await self._safe_edit_message(
            query,
            context,
            OperationsMessages.Error.SYSTEM_ERROR,
            OperationsKeyboard.back_to_operations(),
        )
```

**Step 3: Remove `_escape_md()` from operations.py**

No longer needed.

**Step 4: Run tests**

```bash
uv run pytest tests/bot/test_operations_handlers.py -v
```
Expected: All tests pass

**Step 5: Commit**

```bash
git add src/bot/handlers/operations.py
git commit -m "refactor: unify operations menu referral display with shared template"
```

---

### Task 5: Full Test Suite Verification

**Step 1: Run full test suite**

```bash
uv run pytest tests/unit tests/bot -v
```
Expected: 381+ tests pass

**Step 2: Run referral-specific tests**

```bash
uv run pytest tests/ -v -k referral
```
Expected: 36+ tests pass

**Step 3: Run linter**

```bash
uv run ruff check src/bot/handlers/referrals.py src/bot/handlers/operations.py src/bot/keyboards/referrals.py src/bot/keyboards/messages_referrals.py
```
Expected: All checks passed

**Step 4: Commit any test fixes**

```bash
git add tests/
git commit -m "test: update tests for HTML parse mode and unified referral display"
```

---

### Task 6: Create PR and Merge

**Step 1: Push branch**

```bash
git push -u origin fix/referral-ux-fixes
```

**Step 2: Create PR**

```bash
gh pr create --title "fix: unify referral UX, fix URL rendering, enable native sharing" --body "..." --base main
```

**Step 3: Merge using PR workflow**

Follow the GitHub PR/Merge Workflow skill.
