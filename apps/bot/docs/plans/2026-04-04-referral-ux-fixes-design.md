# Referral UX Fixes Design

## Problems

1. **Inconsistent messages**: `/referidos` command shows `ReferralsMessages.Menu.REFERRAL_STATS` but the "👥 Referidos" button in operations menu shows `OperationsMessages.Referrals.MENU` — different layouts, different info.

2. **Ugly URL escaping**: Using Markdown with `_escape_md()` produces visible escape characters (`\.`, `\=`) in the displayed URL.

3. **Share button doesn't share**: The "📤 Compartir Enlace" button opens the URL in a browser instead of triggering Telegram's native share dialog.

## Solutions

### 1. Unify Message Format
- Operations menu `show_referrals()` reuses `ReferralsMessages.Menu.REFERRAL_STATS` template
- Operations menu reuses `ReferralsKeyboard.menu()` keyboard
- Remove duplicate `OperationsMessages.Referrals.MENU` (or keep for backward compat)

### 2. Switch to HTML Parse Mode
- Change `parse_mode="Markdown"` → `parse_mode="HTML"`
- Update message templates to use HTML tags: `<b>`, `<code>`, `<a>`
- URLs no longer need escaping — underscores render correctly

### 3. Native Telegram Share
- Change share button from `url=referral_link` to `switch_inline_query="message_text"`
- Pre-written message: "🎯 Únete a usipipo VPN gratis con mi enlace: https://t.me/usipipobot?start=CODE"
- Opens Telegram chat selector for native sharing

## Files Changed

- `src/bot/handlers/referrals.py` — HTML parse mode, switch_inline_query
- `src/bot/handlers/operations.py` — Reuse ReferralsMessages + ReferralsKeyboard
- `src/bot/keyboards/referrals.py` — switch_inline_query for share button
- `src/bot/keyboards/messages_referrals.py` — Convert Markdown → HTML templates
- `tests/bot/test_referrals_handlers.py` — Update assertions for HTML
