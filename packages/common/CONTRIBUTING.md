# Contributing to uSipipo Commons

Thank you for your interest in contributing to uSipipo Commons! This guide will help you set up your development environment, understand our code style, and submit high-quality contributions.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup Development Environment](#setup-development-environment)
- [Code Style](#code-style)
  - [Ruff](#ruff)
  - [MyPy](#mypy)
  - [Formatting](#formatting)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Coverage Requirements](#coverage-requirements)
  - [Test Structure](#test-structure)
- [Commit Messages](#commit-messages)
  - [Conventional Commits](#conventional-commits)
  - [Examples](#examples)
- [Pull Requests](#pull-requests)
  - [Before Submitting](#before-submitting)
  - [PR Template](#pr-template)
- [Release Process](#release-process)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - Required for all uSipipo projects
- **uv** - Fast Python package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git** - Version control

Optional but recommended:
- **Docker** - For containerized testing
- **VS Code** or **PyCharm** - IDE with Python support

### Setup Development Environment

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/uSipipo-Team/usipipo-commons.git
   cd usipipo-commons
   ```

2. **Install Python 3.13 (if not already installed):**

   ```bash
   uv python install 3.13
   ```

3. **Install dependencies:**

   ```bash
   uv sync --dev
   ```

   This creates a virtual environment and installs all development dependencies including:
   - `pytest` - Testing framework
   - `pytest-cov` - Coverage reporting
   - `mypy` - Static type checking
   - `ruff` - Fast Python linter

4. **Verify your setup:**

   ```bash
   # Run tests
   uv run pytest

   # Run linter
   uv run ruff check .

   # Run type checker
   uv run mypy .
   ```

---

## Code Style

We enforce strict code quality standards using automated tools. All code must pass these checks before merging.

### Ruff

We use [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting. It's configured in `pyproject.toml` with:

- **Line length:** 100 characters
- **Target version:** Python 3.13
- **Quote style:** Double quotes
- **Import sorting:** Enabled

**Commands:**

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### MyPy

We use [MyPy](https://mypy.readthedocs.io/) for static type checking. All public functions and methods must have type hints.

**Commands:**

```bash
# Run type checking
uv run mypy .

# Run with verbose output
uv run mypy usipipo_commons/ --verbose
```

**Type Hint Examples:**

```python
# ✅ Good: Proper type hints
def validate_telegram_id(telegram_id: int) -> bool:
    """Validate that telegram_id is positive."""
    return telegram_id > 0

def format_bytes(bytes_count: int) -> str:
    """Format bytes to human-readable string."""
    ...

# ❌ Bad: Missing type hints
def validate_telegram_id(telegram_id):
    return telegram_id > 0
```

### Formatting

Code formatting is automatically handled by Ruff. Before committing:

```bash
# Format all files
uv run ruff format .

# Fix linting issues
uv run ruff check . --fix
```

**Style Guidelines:**
- Use 4 spaces for indentation (no tabs)
- Use double quotes for strings
- Maximum line length: 100 characters
- Use trailing commas in multi-line structures
- Import order: standard library → third-party → local imports

---

## Testing

We use [pytest](https://docs.pytest.org/) for testing. All new features and bug fixes must include tests.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=usipipo_commons --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_domain_entities.py

# Run specific test function
uv run pytest tests/test_domain_entities.py::test_user_creation

# Run tests matching a pattern
uv run pytest -k "test_user"

# Run tests in parallel (requires pytest-xdist)
uv run pytest -n auto
```

### Coverage Requirements

- **Minimum coverage:** 80%
- **Critical paths:** 100% (domain entities, validation logic)

**Check coverage:**

```bash
uv run pytest --cov=usipipo_commons --cov-fail-under=80
```

**Generate HTML coverage report:**

```bash
uv run pytest --cov=usipipo_commons --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure

We follow the **Arrange-Act-Assert (AAA)** pattern for all tests:

```python
import pytest
from usipipo_commons.domain.entities import User, VpnKey
from usipipo_commons.domain.enums import VpnType, KeyStatus


class TestUserCreation:
    """Test suite for User entity creation and validation."""

    def test_create_user_with_valid_telegram_id(self) -> None:
        """
        Test that a user can be created with a valid telegram_id.
        
        AAA Pattern:
        - Arrange: Set up test data
        - Act: Execute the operation
        - Assert: Verify the results
        """
        # Arrange
        telegram_id = 123456789
        username = "test_user"
        
        # Act
        user = User(
            telegram_id=telegram_id,
            username=username,
            balance=0.0
        )
        
        # Assert
        assert user.telegram_id == telegram_id
        assert user.username == username
        assert user.balance == 0.0
        assert user.created_at is not None

    def test_create_user_with_invalid_telegram_id_raises_error(self) -> None:
        """Test that invalid telegram_id raises ValueError."""
        # Arrange
        invalid_telegram_id = -1
        
        # Act & Assert
        with pytest.raises(ValueError, match="telegram_id must be positive"):
            User(
                telegram_id=invalid_telegram_id,
                username="test_user",
                balance=0.0
            )

    def test_user_add_balance(self) -> None:
        """Test adding balance to user account."""
        # Arrange
        user = User(telegram_id=123456, username="test", balance=10.0)
        amount_to_add = 5.0
        
        # Act
        user.add_balance(amount_to_add)
        
        # Assert
        assert user.balance == 15.0

    def test_user_add_negative_balance_raises_error(self) -> None:
        """Test that adding negative balance raises error."""
        # Arrange
        user = User(telegram_id=123456, username="test", balance=10.0)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Amount must be positive"):
            user.add_balance(-5.0)
```

**Test Naming Convention:**

```
test_<method>_<scenario>_<expected_result>
```

Examples:
- `test_create_user_with_valid_data_succeeds`
- `test_validate_telegram_id_with_negative_number_raises_error`
- `test_user_add_balance_increases_total`

**Test Organization:**

```
tests/
├── test_domain_entities.py      # Entity tests
├── test_schemas.py              # Pydantic schema tests
├── test_constants.py            # Constant value tests
└── test_utils.py                # Utility function tests
```

---

## Commit Messages

### Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for clear, consistent commit messages.

**Format:**

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, semicolons, etc.) |
| `refactor` | Code refactoring (no functional changes) |
| `perf` | Performance improvements |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependencies |
| `ci` | CI/CD configuration changes |
| `build` | Build system or external dependencies |

### Examples

```bash
# Feature
git commit -m "feat: add ConsumptionInvoice entity"
git commit -m "feat(schemas): add CreateConsumptionRequest schema"

# Bug fix
git commit -m "fix: correct validation for telegram_id"
git commit -m "fix(domain): handle edge case in format_bytes utility"

# Documentation
git commit -m "docs: update README with installation instructions"
git commit -m "docs: add contributing guide"

# Refactoring
git commit -m "refactor: extract validation logic to separate module"

# Testing
git commit -m "test: add unit tests for User entity"
git commit -m "test(schemas): increase coverage for PaymentResponse"

# Chores
git commit -m "chore: update pyproject.toml dependencies"
git commit -m "chore(deps): bump pydantic from 2.11.0 to 2.12.0"

# CI/CD
git commit -m "ci: add coverage reporting to GitHub Actions"
```

**Multi-line commit example:**

```bash
git commit -m "feat: add subscription plan entities

Add SubscriptionPlan and SubscriptionTransaction entities
to support recurring billing functionality.

- Add SubscriptionPlan with monthly/yearly billing cycles
- Add SubscriptionTransaction for tracking payments
- Include proration logic for plan changes

Closes #42"
```

---

## Pull Requests

### Before Submitting

Before submitting a pull request, ensure:

- [ ] **Code compiles:** `uv run mypy .` passes with no errors
- [ ] **Tests pass:** `uv run pytest` passes all tests
- [ ] **Coverage met:** `uv run pytest --cov --cov-fail-under=80` passes
- [ ] **Linting clean:** `uv run ruff check .` shows no issues
- [ ] **Formatting applied:** `uv run ruff format .` has been run
- [ ] **Commits follow convention:** All commit messages use Conventional Commits
- [ ] **Changes are focused:** PR addresses a single feature/fix
- [ ] **Documentation updated:** README, docstrings, or docs/ updated if needed
- [ ] **Changelog updated:** Changes documented in CHANGELOG.md (if applicable)

### PR Template

When creating a pull request, use the following template:

```markdown
## Description

Brief description of the changes in this PR.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📝 Documentation update
- [ ] 🎨 Style/formatting changes
- [ ] ♻️ Code refactoring
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test updates
- [ ] 🔧 CI/CD or build changes

## Related Issues

Closes #<issue_number>

## Testing

Describe how you tested these changes:

```bash
# Example commands run
uv run pytest
uv run mypy .
uv run ruff check .
```

## Checklist

- [ ] My code follows the project's code style
- [ ] I have added tests that prove my fix/feature works
- [ ] All tests pass locally with my changes
- [ ] I have updated the documentation accordingly
- [ ] I have checked for potential breaking changes
- [ ] My changes generate no new warnings or errors

## Screenshots (if applicable)

Add screenshots if your changes affect the user-facing API or schemas.

## Additional Notes

Any additional information reviewers should know.
```

---

## Release Process

Releases are managed by maintainers. The process follows semantic versioning (SemVer):

### Version Numbering

```
MAJOR.MINOR.PATCH
```

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Release Steps

1. **Update version in `pyproject.toml`:**

   ```toml
   [project]
   name = "usipipo-commons"
   version = "0.12.0"  # Update this
   ```

2. **Update `CHANGELOG.md`:**

   ```markdown
   ## [0.12.0] - 2026-03-22

   ### Added
   - New ConsumptionInvoice entity
   - Subscription plan support

   ### Changed
   - Updated pydantic to 2.12.0

   ### Fixed
   - Edge case in format_bytes utility
   ```

3. **Create release commit:**

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: release version 0.12.0"
   git tag -a "v0.12.0" -m "Release version 0.12.0"
   ```

4. **Push changes:**

   ```bash
   git push origin main
   git push origin v0.12.0
   ```

5. **Build package:**

   ```bash
   uv clean
   uv build
   ```

6. **Publish to PyPI:**

   ```bash
   uv publish
   ```

7. **Create GitHub Release:**
   - Go to repository Releases page
   - Create new release from tag `v0.12.0`
   - Copy changelog entries to release notes
   - Attach built artifacts (`.whl`, `.tar.gz`)

---

## Questions?

If you have questions or need help:

- Check existing [issues](https://github.com/uSipipo-Team/usipipo-commons/issues)
- Read the [README.md](README.md)
- Review [CHANGELOG.md](CHANGELOG.md) for version history
- Contact: dev@usipipo.com

Thank you for contributing to uSipipo Commons! 🚀
