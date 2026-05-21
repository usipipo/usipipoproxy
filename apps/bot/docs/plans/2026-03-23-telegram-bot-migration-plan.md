# [Telegram Bot Migration - Phase 1] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate basic commands (/start, /help, /menu) to a lightweight Telegram Bot client.

**Architecture:** The bot is a stateless client interacting with the Backend API (v0.9.0) via HTTP.

**Tech Stack:** `python-telegram-bot`, `httpx` (for API client).

---

### Task 1: Initialize Project Structure

**Files:**
- Create: `src/infrastructure/api_client.py`
- Create: `src/bot/handlers/basic.py`
- Create: `src/bot/keyboards/main.py`
- Create: `tests/bot/test_handlers.py`

**Step 1: Create directories**
Run: `mkdir -p src/bot/handlers src/bot/keyboards src/infrastructure`

**Step 2: Initialize files**
(Empty files for now)

**Step 3: Commit**
Run: `git add . && git commit -m "chore: setup project structure"`

---

### Task 2: Implement HTTP API Client

**Files:**
- Modify: `src/infrastructure/api_client.py`
- Test: `tests/test_api_client.py`

**Step 1: Write failing test**
```python
import pytest
from src.infrastructure.api_client import APIClient

def test_api_client_initialization():
    client = APIClient(base_url="http://localhost:8001")
    assert client.base_url == "http://localhost:8001"
```

**Step 2: Run test (Expect fail)**
Run: `pytest tests/test_api_client.py`

**Step 3: Implement minimal code**
```python
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
```

**Step 4: Run test (Expect pass)**
Run: `pytest tests/test_api_client.py`

**Step 5: Commit**
Run: `git add . && git commit -m "feat: implement API client"`

---

### Task 3: Migrate `/start` command

**Files:**
- Modify: `src/bot/handlers/basic.py`
- Modify: `src/main.py`
- Test: `tests/bot/test_handlers.py`

**Step 1: Write failing test**
```python
from telegram import Update
from src.bot.handlers.basic import start_command

async def test_start_command():
    # Mocking telegram structures
    ...
```

**Step 2: Implement**
...

**Step 3: Commit**
...

---

**Plan complete and saved to `docs/plans/2026-03-23-telegram-bot-migration-plan.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration.

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints.

**Which approach?**
