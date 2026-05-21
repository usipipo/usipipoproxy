# Backend Docker Release + Test Restructure Design

**Date:** 2026-04-05
**Status:** Approved

## Overview

Add automated Docker image build/push to ghcr.io on tag releases, and restructure tests directory for proper unit/integration/e2e separation.

## 1. Release Workflow

**Trigger:** Push of tag `v*`

**Jobs (all inline):**
- Lint (Ruff)
- Type Check (Mypy)
- Test (Pytest - unit tests only)
- Security (Bandit)
- Docker build/push to `ghcr.io/usipipo-team/usipipo-apps-backend`

**Image tags:** `v0.X.0` + `latest`

## 2. Test Restructure

Move non-unit tests out of `tests/unit/` path and consolidate:

```
tests/
├── unit/
│   ├── repositories/     (from tests/unit/repositories/)
│   ├── services/         (from tests/unit/services/)
│   ├── schemas/          (from tests/shared/schemas/)
│   └── ...               (from tests/unit/)
├── integration/          (already structured)
└── e2e/                  (already structured)
```

**Moves:**
- `tests/infrastructure/` → `tests/unit/infrastructure/`
- `tests/shared/schemas/` → `tests/unit/schemas/`
- `tests/shared/test_referral_schemas.py` → `tests/unit/test_referral_schemas.py`
- `tests/test_main.py` → `tests/unit/test_main.py`

**CI update:** Both CI and Release workflows run `pytest tests/unit -v` only.

## 3. Dockerfile

Already optimized (multi-stage). No changes needed.

## Files
- **Create:** `.github/workflows/release.yml`
- **Modify:** `.github/workflows/ci.yml` (run only unit tests)
- **Move:** ~20 test files to proper unit/ paths
- **Create:** `__init__.py` files for new test packages
