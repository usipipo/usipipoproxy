#!/usr/bin/env python3
"""
Test script to verify Telegram Bot <-> Backend integration.

This script tests:
1. Backend API connectivity
2. Auto-registration endpoint
3. User profile endpoint
4. VPN key management endpoints
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://usipipo.duckdns.org")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
TELEGRAM_ID = int(os.getenv("ADMIN_ID", "1058749165"))

print("=" * 70)
print("uSipipo Bot <-> Backend Integration Test")
print("=" * 70)
print(f"Backend URL: {BACKEND_URL}{API_PREFIX}")
print(f"Test Telegram ID: {TELEGRAM_ID}")
print("=" * 70)


async def test_backend_connectivity():
    """Test 1: Check if backend is reachable."""
    print("\n[TEST 1] Backend Connectivity")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test root endpoint (Swagger docs)
            response = await client.get(f"{BACKEND_URL}{API_PREFIX}")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                print("✅ Backend is reachable")
                return True
            else:
                print(f"ℹ️ Backend returned status: {response.status_code}")
                # Continue anyway - API might still work
                return True
        except httpx.ConnectError as e:
            print(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_auto_registration():
    """Test 2: Auto-registration endpoint."""
    print("\n[TEST 2] Auto-Registration Endpoint (/auth/telegram/auto-register)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}{API_PREFIX}/auth/telegram/auto-register",
                json={"telegram_id": TELEGRAM_ID},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code in [200, 201]:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Access Token (first 50 chars): {data.get('access_token', '')[:50]}...")
                print(f"Expires In: {data.get('expires_in')}")
                print("✅ Auto-registration successful")
                return data.get("access_token")
            elif response.status_code == 409:
                print("ℹ️ User already exists (this is OK)")
                # Try to login instead
                return await test_login()
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_login():
    """Test login endpoint for existing user."""
    print("\n[TEST 2b] Login Endpoint")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}{API_PREFIX}/auth/login",
                json={"telegram_id": TELEGRAM_ID},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Access Token (first 50 chars): {data.get('access_token', '')[:50]}...")
                print("✅ Login successful")
                return data.get("access_token")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_user_profile(access_token: str):
    """Test 3: Get user profile."""
    print("\n[TEST 3] User Profile Endpoint (/users/me)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BACKEND_URL}{API_PREFIX}/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"User ID: {data.get('id')}")
                print(f"Telegram ID: {data.get('telegram_id')}")
                print(f"Username: {data.get('username')}")
                print(f"Plan: {data.get('balance_gb')} GB balance")
                print("✅ User profile retrieved")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_vpn_keys_list(access_token: str):
    """Test 4: List VPN keys."""
    print("\n[TEST 4] VPN Keys List Endpoint (/vpn/keys)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BACKEND_URL}{API_PREFIX}/vpn/keys",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Number of keys: {len(data)}")
                for key in data[:3]:  # Show first 3 keys
                    print(f"  - {key.get('name')} ({key.get('key_type')})")
                print("✅ VPN keys listed")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_create_vpn_key(access_token: str):
    """Test 5: Create VPN key."""
    print("\n[TEST 5] Create VPN Key Endpoint (/vpn/keys)")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}{API_PREFIX}/vpn/keys",
                json={
                    "name": "test-integration-key",
                    "vpn_type": "wireguard",
                    "data_limit_gb": 1.0,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code in [200, 201]:
                data = response.json()
                print(f"Key ID: {data.get('id')}")
                print(f"Key Name: {data.get('name')}")
                print(f"Key Type: {data.get('key_type')}")
                print("✅ VPN key created")
                return data.get("id")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_delete_vpn_key(access_token: str, key_id: str):
    """Test 6: Delete VPN key."""
    print("\n[TEST 6] Delete VPN Key Endpoint (/vpn/keys/{id})")
    print("-" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(
                f"{BACKEND_URL}{API_PREFIX}/vpn/keys/{key_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            print(f"Status Code: {response.status_code}")

            if response.status_code in [200, 204]:
                print("✅ VPN key deleted")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def main():
    """Run all tests."""
    results = {
        "connectivity": False,
        "auth": False,
        "profile": False,
        "list_keys": False,
        "create_key": False,
        "delete_key": False,
    }

    # Test 1: Connectivity
    results["connectivity"] = await test_backend_connectivity()

    if not results["connectivity"]:
        print("\n" + "=" * 70)
        print("❌ BACKEND NOT REACHABLE - Stopping tests")
        print("=" * 70)
        return results

    # Test 2: Auth
    access_token = await test_auto_registration()
    results["auth"] = access_token is not None

    if not results["auth"]:
        print("\n" + "=" * 70)
        print("❌ AUTH FAILED - Stopping tests")
        print("=" * 70)
        return results

    # Test 3: Profile
    results["profile"] = await test_user_profile(access_token)

    # Test 4: List Keys
    results["list_keys"] = await test_vpn_keys_list(access_token)

    # Test 5: Create Key
    key_id = await test_create_vpn_key(access_token)
    results["create_key"] = key_id is not None

    # Test 6: Delete Key (cleanup)
    if key_id:
        results["delete_key"] = await test_delete_vpn_key(access_token, key_id)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")

    all_passed = all(results.values())
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {sum(not v for v in results.values())} TEST(S) FAILED")
    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(main())
