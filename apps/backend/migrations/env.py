from logging.config import fileConfig
from urllib.parse import urlparse, urlunparse

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.infrastructure.persistence.database import Base

# Import ALL models so Alembic can detect them
from src.infrastructure.persistence.models import (  # noqa: F401
    ConsumptionBillingModel,
    ConsumptionInvoiceModel,
    CryptoOrderModel,
    CryptoTransactionModel,
    DataPackageModel,
    PaymentModel,
    ReferralModel,
    SubscriptionPlanModel,
    SubscriptionTransactionModel,
    UserModel,
    VpnKeyModel,
    WalletModel,
    WalletPoolModel,
    WebhookTokenModel,
)
from src.shared.config import settings

config = context.config


def get_sync_url(async_url: str) -> str:
    """Convert asyncpg URL to psycopg2 sync URL for Alembic.

    For Supabase pooler connections (postgres.PROJECT_REF@*.pooler.supabase.com),
    rewrites to a direct database connection (postgres@db.PROJECT_REF.supabase.co).
    Direct connections avoid PgBouncer/Supavisor transaction-mode limitations
    that can break alembic's atomic version tracking, especially with merge
    revisions and data migrations that use op.get_bind().
    """
    url = async_url.replace("+asyncpg", "")

    # Detect Supabase pooler: user contains postgres.PROJECT_REF and host is *.pooler.supabase.com
    parsed = urlparse(url)
    if "pooler.supabase.com" in parsed.hostname or "pooler.supabase.com" in str(parsed.hostname):
        # Extract project ref from username (format: postgres.PROJECT_REF)
        username = parsed.username
        if username and username.startswith("postgres."):
            project_ref = username.split(".", 1)[1]
            # Build direct connection URL: replace pooler host with direct db host
            # Direct Supabase connection: db.PROJECT_REF.supabase.co:5432
            direct_host = f"db.{project_ref}.supabase.co"
            # Construct new netloc: keep username:password, replace host:port
            direct_netloc = f"{parsed.username}:{parsed.password}@{direct_host}:5432"
            url = urlunparse(parsed._replace(netloc=direct_netloc))

    return url


sync_url = get_sync_url(settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    cfg = config.get_section(config.config_ini_section, {})

    connect_args = {}
    if "supabase.co" in sync_url or "supabase.com" in sync_url:
        connect_args["sslmode"] = "require"

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
