# E2E Test Framework for VPN Key Operations

## Overview

This directory contains end-to-end (E2E) tests for the VPN key management system. These tests verify the complete flow from API calls → Backend → Agent (mocked) → VPN config generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      E2E Test Flow                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Test       │  HTTP   │   FastAPI    │  HTTP   │   Mocked     │
│   Client     │ ──────▶ │   Backend    │ ──────▶ │   Agent API  │
│  (httpx)     │         │  (Real)      │         │   (respx)    │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │                        │                        │
       ▼                        ▼                        ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│ Auth Headers │         │ Test SQLite  │         │ Mocked       │
│ (JWT tokens) │         │ Database     │         │ Responses    │
└──────────────┘         └──────────────┘         └──────────────┘
```

## Directory Structure

```
tests/e2e/
├── __init__.py
├── conftest.py                    # Pytest fixtures
├── factories/
│   ├── __init__.py
│   ├── user_factory.py            # User test data factory
│   ├── vpn_server_factory.py      # VPN server factory
│   └── vpn_key_factory.py         # VPN key factory
├── test_vpn_key_creation_flow.py  # Creation tests
├── test_vpn_key_deletion_flow.py  # Deletion tests
└── test_vpn_key_list_operations.py # List/retrieve tests
```

## Running Tests

### Prerequisites

Install dev dependencies:

```bash
cd usipipo-backend
uv sync --group dev
```

### Run All E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with coverage
pytest tests/e2e/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/e2e/test_vpn_key_creation_flow.py -v

# Run specific test
pytest tests/e2e/test_vpn_key_creation_flow.py::TestVpnKeyCreationFlow::test_create_wireguard_key_happy_path -v

# Run with logging output
pytest tests/e2e/ -v -s

# Run and stop on first failure
pytest tests/e2e/ -v -x
```

## Test Coverage

### Creation Flow (`test_vpn_key_creation_flow.py`)

| Test | Description | Status |
|------|-------------|--------|
| `test_create_wireguard_key_happy_path` | Create WireGuard key successfully | ✅ |
| `test_create_outline_key_happy_path` | Create Outline key successfully | ✅ |
| `test_create_key_auto_select_server` | Auto-select server when not specified | ✅ |
| `test_create_key_invalid_name_too_short` | Name < 3 chars rejected | ✅ |
| `test_create_key_invalid_name_special_chars` | Shell injection blocked | ✅ |
| `test_create_key_duplicate_name_case_insensitive` | "Home" vs "home" rejected | ✅ |
| `test_create_key_agent_offline` | 503 when agent unreachable | ✅ |
| `test_create_key_rate_limit` | 429 on 11th request | ⏭️ (skipped in tests) |

### Deletion Flow (`test_vpn_key_deletion_flow.py`)

| Test | Description | Status |
|------|-------------|--------|
| `test_delete_wireguard_key_happy_path` | Delete WireGuard key | ✅ |
| `test_delete_outline_key_happy_path` | Delete Outline key | ✅ |
| `test_delete_key_idempotent` | Delete twice succeeds | ✅ |
| `test_delete_key_unauthorized` | Can't delete other's key | ✅ |
| `test_delete_key_not_found` | Delete non-existent key | ✅ |
| `test_delete_key_agent_offline` | 503 when agent offline | ✅ |

### List Operations (`test_vpn_key_list_operations.py`)

| Test | Description | Status |
|------|-------------|--------|
| `test_list_user_keys` | List multiple keys | ✅ |
| `test_list_keys_multiple_types` | Mixed WireGuard + Outline | ✅ |
| `test_list_keys_empty` | Empty list for new user | ✅ |
| `test_get_single_key` | Get single key by ID | ✅ |
| `test_get_key_includes_server_info` | Server details included | ✅ |

**Total: 18 test scenarios**

## Fixtures

### Core Fixtures (`conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `test_settings` | Session | Test settings with SQLite |
| `test_database` | Function | In-memory SQLite database |
| `client` | Function | Async HTTP test client |
| `mocked_agent_api` | Function | Mocked agent HTTP API (respx) |
| `test_user` | Function | Test user in database |
| `test_vpn_server` | Function | Test VPN server |
| `auth_headers` | Function | JWT auth headers |
| `clean_database` | Function | Clean DB between tests |

### Factories

```python
from tests.e2e.factories.user_factory import UserFactory
from tests.e2e.factories.vpn_server_factory import VpnServerFactory
from tests.e2e.factories.vpn_key_factory import VpnKeyFactory

# Create test user
user = UserFactory.create(
    telegram_id=123456,
    username="testuser"
)

# Create test server
server = VpnServerFactory.create(
    name="Test Server",
    location="US"
)

# Create test key
key = VpnKeyFactory.create(
    user_id=user.id,
    server_id=server.id,
    key_type=KeyType.WIREGUARD
)
```

## Mock Strategy

### What's Mocked

- ✅ Agent HTTP API (using `respx`)
  - Health check endpoint
  - Outline key create/delete
  - WireGuard peer create/delete

### What's Real

- ✅ FastAPI application
- ✅ Service layer logic
- ✅ Validation logic
- ✅ Database operations (SQLite)
- ✅ Authentication (JWT)

### Mock Response Example

```python
# Mock Outline key creation
mock.post("http://test-agent/outline/keys").mock(
    return_value=respx.models.Response(
        status_code=201,
        json={
            "id": "outline-key-123",
            "name": "test-key",
            "access_url": "ss://test-access-url"
        }
    )
)
```

## Writing New Tests

### Template

```python
import pytest
from httpx import AsyncClient

class TestMyNewFeature:

    @pytest.mark.asyncio
    async def test_feature_happy_path(
        self,
        client: AsyncClient,
        test_user: UserModel,
        mocked_agent_api,
        auth_headers: dict
    ):
        """Test description."""
        # Arrange
        payload = {...}

        # Act
        response = await client.post(
            "/api/v1/vpn/endpoint",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["field"] == "expected_value"
```

### Best Practices

1. **Test Independence**: Each test must be independent (no shared state)
2. **Use Fixtures**: Always use provided fixtures for setup
3. **Mock External Services**: Never call real agent API
4. **Assert Everything**: Check status codes, response data, and database state
5. **Descriptive Names**: Use clear test method names
6. **Arrange-Act-Assert**: Follow AAA pattern

## Troubleshooting

### Common Issues

**Issue**: Test fails with "no such table" error
**Solution**: Ensure `test_database` fixture is used (it creates tables)

**Issue**: Mock not being called
**Solution**: Check URL matches exactly (including trailing slashes)

**Issue**: Rate limiting interfering with tests
**Solution**: Rate limiting is disabled in test settings

**Issue**: Authentication errors
**Solution**: Always use `auth_headers` fixture for authenticated requests

### Debug Mode

```bash
# Run with verbose logging
pytest tests/e2e/ -v --log-cli-level=DEBUG

# Run single test with pdb
pytest tests/e2e/test_file.py::test_name -s --pdb
```

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run E2E Tests
  run: |
    cd usipipo-backend
    uv sync --group dev
    pytest tests/e2e/ -v --tb=short
```

## Future Enhancements

- [ ] Add performance benchmarks
- [ ] Add chaos testing (random agent failures)
- [ ] Add concurrent user tests
- [ ] Add database migration tests
- [ ] Add rollback scenario tests
- [ ] Integration with test reporting (Allure, HTML reports)

## Dependencies

- `pytest>=8.0.0` - Test framework
- `pytest-asyncio>=0.23.0` - Async test support
- `respx>=0.21.0` - HTTPX mocking
- `factory-boy>=3.3.0` - Test data factories
- `aiosqlite>=0.20.0` - SQLite for tests

## Related Documentation

- [SAGA Rollback Implementation](../../SAGA_ROLLBACK_IMPLEMENTATION.md)
- [Security Audit Report](../../SECURITY_AUDIT_REPORT.md)
- [API Documentation](../src/infrastructure/api/README.md)
