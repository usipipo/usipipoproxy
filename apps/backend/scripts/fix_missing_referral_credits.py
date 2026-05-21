"""
Compensation script for users missing referral credits.

Finds users who were referred but didn't receive their 50-credit new user bonus,
and referrers who didn't receive their 100-credit per-referral bonus.

Usage:
    uv run python scripts/fix_missing_referral_credits.py          # dry run (report only)
    uv run python scripts/fix_missing_referral_credits.py --apply  # apply fixes
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text

from src.infrastructure.persistence.models.user_model import UserModel
from src.shared.config import settings


async def find_affected_users(session) -> dict:
    """Find users missing referral credits."""
    result = {}

    # 1. Referred users with 0 credits (should have REFERRAL_BONUS_NEW_USER = 50)
    stmt_new_users = select(UserModel).where(
        UserModel.referred_by.isnot(None),
        UserModel.referral_credits == 0,
    )
    new_users_result = await session.execute(stmt_new_users)
    new_users_without_credits = new_users_result.scalars().all()

    result["new_users_missing_credits"] = [
        {
            "user_id": str(u.id),
            "telegram_id": u.telegram_id,
            "referred_by": str(u.referred_by),
            "current_credits": u.referral_credits,
            "expected_credits": settings.REFERRAL_BONUS_NEW_USER,
        }
        for u in new_users_without_credits
    ]

    # 2. Referrers whose credits don't match their referral count
    stmt_referrers = text("""
        SELECT
            u.id as referrer_id,
            u.telegram_id,
            u.referral_credits,
            COUNT(r.id) as referral_count,
            (COUNT(r.id) * :credits_per_referral) as expected_credits
        FROM users u
        INNER JOIN referrals r ON u.id = r.referrer_id
        GROUP BY u.id, u.telegram_id, u.referral_credits
        HAVING u.referral_credits != (COUNT(r.id) * :credits_per_referral)
    """)
    referrers_result = await session.execute(
        stmt_referrers, {"credits_per_referral": settings.REFERRAL_CREDITS_PER_REFERRAL}
    )
    referrers_with_mismatch = referrers_result.fetchall()

    result["referrers_credit_mismatch"] = [
        {
            "referrer_id": str(r.referrer_id),
            "telegram_id": r.telegram_id,
            "current_credits": r.referral_credits,
            "referral_count": r.referral_count,
            "expected_credits": r.expected_credits,
        }
        for r in referrers_with_mismatch
    ]

    return result


async def apply_fixes(session, affected: dict) -> int:
    """Apply credit fixes. Returns count of fixed users."""
    fixed_count = 0

    # Fix new users missing credits (idempotent: only fixes where credits == 0)
    for user_data in affected["new_users_missing_credits"]:
        stmt = select(UserModel).where(UserModel.id == user_data["user_id"])
        result = await session.execute(stmt)
        user = result.scalar_one()
        user.referral_credits = settings.REFERRAL_BONUS_NEW_USER
        fixed_count += 1
        print(
            f"  Fixed user {user_data['user_id']}: 0 -> {settings.REFERRAL_BONUS_NEW_USER} credits"
        )

    # Fix referrer credit mismatches
    for ref_data in affected["referrers_credit_mismatch"]:
        stmt = select(UserModel).where(UserModel.id == ref_data["referrer_id"])
        result = await session.execute(stmt)
        referrer = result.scalar_one()
        referrer.referral_credits = ref_data["expected_credits"]
        fixed_count += 1
        print(
            f"  Fixed referrer {ref_data['referrer_id']}: "
            f"{ref_data['current_credits']} -> {ref_data['expected_credits']} credits"
        )

    return fixed_count


async def main(dry_run: bool = True):
    """Main entry point."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            affected = await find_affected_users(session)

            new_users_count = len(affected["new_users_missing_credits"])
            referrers_count = len(affected["referrers_credit_mismatch"])
            total_affected = new_users_count + referrers_count

            print(f"\n{'=' * 60}")
            print("Referral Credit Compensation Report")
            print(f"{'=' * 60}")
            print(f"\nNew users missing credits: {new_users_count}")
            for u in affected["new_users_missing_credits"]:
                print(f"  - telegram_id={u['telegram_id']}, referred_by={u['referred_by']}")

            print(f"\nReferrers with credit mismatch: {referrers_count}")
            for r in affected["referrers_credit_mismatch"]:
                print(
                    f"  - telegram_id={r['telegram_id']}, "
                    f"has={r['current_credits']}, expected={r['expected_credits']}"
                )

            if total_affected == 0:
                print("\nNo affected users found. All referral credits are correct.")
                return

            if dry_run:
                print(f"\n{'=' * 60}")
                print(f"DRY RUN -- {total_affected} users would be affected.")
                print("Run with --apply to apply fixes.")
                print(f"{'=' * 60}")
            else:
                print(f"\nApplying fixes for {total_affected} users...")
                fixed = await apply_fixes(session, affected)
                await session.commit()
                print(f"\nFixed {fixed} users successfully.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix missing referral credits")
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default: dry run)")
    args = parser.parse_args()

    asyncio.run(main(dry_run=not args.apply))
