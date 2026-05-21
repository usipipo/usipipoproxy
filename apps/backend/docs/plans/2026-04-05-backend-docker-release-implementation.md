# Backend Docker Release + Test Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add automated Docker release workflow to ghcr.io and restructure tests directory for proper unit/integration/e2e separation.

**Architecture:** Release workflow with inline CI jobs (ruff, mypy, pytest unit, bandit) + Docker build/push. Tests reorganized into unit/, integration/, e2e/ with CI running only unit tests.

**Tech Stack:** Python 3.13, FastAPI, uv, pytest, Docker, GitHub Actions, ghcr.io

---

## Task 1: Restructure Tests Directory

**Files to move:**
- `tests/infrastructure/` → `tests/unit/infrastructure/`
- `tests/shared/schemas/` → `tests/unit/schemas/`
- `tests/shared/test_referral_schemas.py` → `tests/unit/test_referral_schemas.py`
- `tests/test_main.py` → `tests/unit/test_main.py`

**Steps:**

1. Create missing directories:
```bash
mkdir -p tests/unit/infrastructure tests/unit/schemas
```

2. Move files:
```bash
mv tests/infrastructure tests/unit/
mv tests/shared/schemas tests/unit/
mv tests/shared/test_referral_schemas.py tests/unit/
mv tests/test_main.py tests/unit/
```

3. Create `__init__.py` files:
```bash
touch tests/unit/infrastructure/__init__.py
touch tests/unit/schemas/__init__.py
```

4. Clean up empty dirs:
```bash
rmdir tests/shared 2>/dev/null || true
```

5. Verify unit tests pass:
```bash
uv run pytest tests/unit -v --tb=short
```
Expected: All unit tests pass

6. Commit:
```bash
git add tests/
git commit -m "refactor: restructure tests directory for unit/integration/e2e separation"
```

---

## Task 2: Create Release Workflow

**Files:**
- Create: `.github/workflows/release.yml`

**Step 1: Create release.yml**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  lint:
    name: Lint (Ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: |
          uv sync
          uv pip install ruff
      - run: uv run ruff check src/ tests/
      - run: uv run ruff format src/ tests/ --check

  type-check:
    name: Type Check (Mypy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: |
          uv sync
          uv pip install mypy
      - run: uv run mypy src/

  test:
    name: Test (Pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: |
          uv sync
          uv pip install pytest pytest-asyncio
      - run: uv run pytest tests/unit -v

  security:
    name: Security (Bandit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: |
          uv sync
          uv pip install bandit
      - run: uv run bandit -r src/ -ll -ii

  docker:
    needs: [lint, type-check, test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/usipipo-team/usipipo-apps-backend:${{ steps.version.outputs.VERSION }}
            ghcr.io/usipipo-team/usipipo-apps-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Step 2: Commit**
```bash
git add .github/workflows/release.yml
git commit -m "feat: add Docker release workflow to ghcr.io"
```

---

## Task 3: Update CI Workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

**Step 1: Change pytest command to run only unit tests**

In `ci.yml`, find the test job and change:
```yaml
      - run: uv run pytest -v
```
to:
```yaml
      - run: uv run pytest tests/unit -v
```

**Step 2: Commit**
```bash
git add .github/workflows/ci.yml
git commit -m "ci: run only unit tests in CI workflow"
```

---

## Task 4: Push, PR, Merge, Tag, Release

**Steps:**

1. Push branch and create PR:
```bash
git push -u origin feat/backend-docker-release
gh pr create --base main --head feat/backend-docker-release \
  --title "feat: Docker release workflow + test restructure" \
  --body "## Description\n\n- Add Docker release workflow to ghcr.io\n- Restructure tests: unit/, integration/, e2e/\n- CI runs only unit tests"
```

2. Merge PR (using GitHub PR/Merge Workflow skill)

3. Pull main, create tag, push:
```bash
git pull origin main
git tag -a v0.22.0 -m "Release v0.22.0 - Docker Release + Test Restructure"
git push origin v0.22.0
```

4. Verify workflow passes:
```bash
gh run list --limit 3
```
Expected: Release workflow shows success

---

## Summary Checklist

- [ ] Task 1: Restructure tests directory
- [ ] Task 2: Create Release workflow
- [ ] Task 3: Update CI workflow
- [ ] Task 4: Push, PR, merge, tag, release
