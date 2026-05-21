# Design: Share Button for Referral Message

**Date:** 2026-04-04
**Status:** Approved
**Repository:** usipipo-telegram-bot

## Context

The referral system currently shows stats when user runs `/referidos`, but requires a separate `/invitar` command to get the shareable link. Users need a faster way to share their referral link.

## Goal

Add a "📤 Compartir" button directly to the referral stats message that opens the referral link for sharing.

## Design Decisions

### 1. Message Format Update
**File:** `src/bot/keyboards/messages_referrals.py`

Update `REFERRAL_STATS` to include the referral link in the message text:
- Add line showing the link: `🔗 Tu enlace: https://t.me/usipipobot?start={referral_code}`
- Keep existing stats format intact

### 2. Keyboard Update
**File:** `src/bot/keyboards/referrals.py`

Modify `menu()` to accept optional `referral_link` parameter:
- Add "📤 Compartir Enlace" button as first row when link is provided
- Use `url` parameter with the referral link
- Keep existing buttons (Canjear Créditos, Aplicar Código)

### 3. Handler Update
**File:** `src/bot/handlers/referrals.py`

Update `show_referrals()` method:
- Build referral link from API response: `https://t.me/usipipobot?start={referral_code}`
- Pass link to both message template and keyboard
- No additional API calls needed (uses existing `/referrals/me` endpoint)

## Implementation Plan

1. Update `REFERRAL_STATS` message template to include referral link
2. Modify `ReferralsKeyboard.menu()` to accept and use referral_link parameter
3. Update `ReferralsHandler.show_referrals()` to build link and pass to message/keyboard
4. Run tests to verify no regressions
5. Update tests if needed

## User Flow

```
User: /referidos
Bot: 🎯 Tu Programa de Referidos

     📊 Estadísticas:
     • Código: abc123
     • Total referidos: 5
     • Créditos disponibles: 10
     • Tu enlace: https://t.me/usipipobot?start=abc123

     💡 Beneficios:
     • 1 crédito por cada amigo invitado
     • 5 créditos si tu amigo compra un paquete

     [📤 Compartir Enlace]  ← NEW BUTTON
     [💰 Canjear Créditos]
     [📝 Aplicar Código]
```

## Testing Strategy

- Verify message format includes referral link
- Verify share button opens correct URL
- Verify existing functionality (redeem, apply code) still works
- Run unit tests: `pytest tests/bot/test_referrals_*`

## Rollback Plan

If issues arise:
1. Revert message template to original format
2. Remove referral_link parameter from keyboard
3. Restore original handler logic
