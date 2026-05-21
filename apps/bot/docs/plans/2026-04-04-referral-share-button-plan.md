# Referral Share Button Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a share button to the referral stats message that allows users to share their referral link directly.

**Architecture:** Update the existing referral message template and keyboard to include the referral link and a share button. The link is built from the referral_code returned by the `/referrals/me` API endpoint.

**Tech Stack:** Python 3.13, python-telegram-bot, FastAPI backend

---

### Task 1: Update Referral Message Template

**Files:**
- Modify: `src/bot/keyboards/messages_referrals.py:13-23`

**Step 1: Update REFERRAL_STATS message to include referral link**

```python
REFERRAL_STATS = (
    "🎯 *Tu Programa de Referidos*\n\n"
    "📊 *Estadísticas:*\n"
    "• Código: `{referral_code}`\n"
    "• Total referidos: `{total_referrals}`\n"
    "• Créditos disponibles: `{referral_credits}`\n\n"
    "🔗 *Tu enlace:*\n"
    "{referral_link}\n\n"
    "💡 *Beneficios:*\n"
    "• 1 crédito por cada amigo invitado\n"
    "• 5 créditos si tu amigo compra un paquete\n\n"
    "Comparte tu enlace y gana créditos!"
)
```

**Step 2: Commit**

```bash
git add src/bot/keyboards/messages_referrals.py
git commit -m "feat: add referral link to stats message template"
```

---

### Task 2: Update Referral Keyboard to Accept Link

**Files:**
- Modify: `src/bot/keyboards/referrals.py:9-22`

**Step 1: Update menu() method to accept referral_link parameter**

```python
@staticmethod
def menu(referral_link: str | None = None) -> InlineKeyboardMarkup:
    """Main referrals menu keyboard with optional share button."""
    keyboard = []
    
    # Add share button as first row if referral link is provided
    if referral_link:
        keyboard.append([
            InlineKeyboardButton("📤 Compartir Enlace", url=referral_link),
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
git commit -m "feat: add share button to referral menu keyboard"
```

---

### Task 3: Update Handler to Build and Pass Link

**Files:**
- Modify: `src/bot/handlers/referrals.py:63-85`

**Step 1: Update show_referrals() to build referral link and pass to message/keyboard**

In the `show_referrals()` method, after getting the response from the API:

```python
# Build referral link
referral_code = response["referral_code"]
referral_link = f"https://t.me/usipipobot?start={referral_code}"

# Format message
message = ReferralsMessages.Menu.REFERRAL_STATS.format(
    referral_code=referral_code,
    total_referrals=response["total_referrals"],
    referral_credits=response["referral_credits"],
    referral_link=referral_link,
)

# Send with keyboard
if update.message:
    await update.message.reply_text(
        text=message,
        reply_markup=ReferralsKeyboard.menu(referral_link),
        parse_mode="Markdown",
    )
```

**Step 2: Commit**

```bash
git add src/bot/handlers/referrals.py
git commit -m "feat: pass referral link to message and keyboard in handler"
```

---

### Task 4: Run Tests and Verify

**Files:**
- Test: `tests/bot/test_referrals_handlers.py`
- Test: `tests/bot/test_referrals_keyboards.py`
- Test: `tests/bot/test_referrals_messages.py`

**Step 1: Run existing referral tests**

```bash
cd /home/mowgli/usipipo/usipipo-telegram-bot
pytest tests/bot/test_referrals_handlers.py tests/bot/test_referrals_keyboards.py tests/bot/test_referrals_messages.py -v
```

Expected: Some tests may fail due to the new `referral_link` parameter in the message template and keyboard.

**Step 2: Update tests if needed**

If tests fail, update them to:
- Include `referral_link` in the mock API response
- Update message assertions to match new format
- Update keyboard assertions to check for share button

**Step 3: Re-run tests to verify all pass**

```bash
pytest tests/bot/test_referrals_handlers.py tests/bot/test_referrals_keyboards.py tests/bot/test_referrals_messages.py -v
```

Expected: All tests PASS

**Step 4: Commit test updates (if any)**

```bash
git add tests/
git commit -m "test: update referral tests for share button"
```

---

### Task 5: Integration Test (Manual Verification)

**Step 1: Restart the bot**

```bash
sudo systemctl restart usipipo-telegram-bot
```

**Step 2: Test the flow**

1. Send `/referidos` to the bot
2. Verify message shows:
   - Referral code
   - Total referrals
   - Credits available
   - Referral link (clickable URL)
3. Verify keyboard shows:
   - 📤 Compartir Enlace (first button)
   - 💰 Canjear Créditos
   - 📝 Aplicar Código
4. Click "Compartir Enlace" button → Should open Telegram share dialog

**Step 3: Verify existing functionality**

- Test `/invitar` still works
- Test "Canjear Créditos" still works
- Test "Aplicar Código" still works

---

### Task 6: Final Commit and Push

**Step 1: Ensure all changes are committed**

```bash
git status
```

**Step 2: Push to remote**

```bash
git push origin feature/referral-share-button
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `src/bot/keyboards/messages_referrals.py` | Add `referral_link` to REFERRAL_STATS template |
| `src/bot/keyboards/referrals.py` | Add `referral_link` param to `menu()`, add share button |
| `src/bot/handlers/referrals.py` | Build link and pass to message/keyboard |
| `tests/bot/test_referrals_*.py` | Update tests if needed |

## Expected Output

When user runs `/referidos`:

```
🎯 Tu Programa de Referidos

📊 Estadísticas:
• Código: abc123
• Total referidos: 0
• Créditos disponibles: 0

🔗 Tu enlace:
https://t.me/usipipobot?start=abc123

💡 Beneficios:
• 1 crédito por cada amigo invitado
• 5 créditos si tu amigo compra un paquete

Comparte tu enlace y gana créditos!

[📤 Compartir Enlace]
[💰 Canjear Créditos]
[📝 Aplicar Código]
```
