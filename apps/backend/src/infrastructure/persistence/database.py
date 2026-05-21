"""Configuración de base de datos SQLAlchemy (sync)."""

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from src.shared.config import settings

logger = logging.getLogger(__name__)


def get_execute_rowcount(result: Result) -> int:
    """
    Obtiene rowcount de un resultado de execute().

    Args:
        result: Resultado de session.execute()

    Returns:
        int: Cantidad de filas afectadas (0 si es None)
    """
    return getattr(result, "rowcount", 0) or 0


class Base(DeclarativeBase):
    """Clase base para modelos SQLAlchemy."""
    pass


# Configurar SSL para conexiones Supabase
connect_args = {}
if "supabase.co" in settings.DATABASE_URL or "supabase.com" in settings.DATABASE_URL:
    connect_args["sslmode"] = "require"

# Crear engine síncrono
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.is_development and settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=10,
    pool_timeout=settings.DB_TIMEOUT,
    connect_args=connect_args,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.

    Yields:
        Session: Sesión síncrona de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Verifica conexión a BD al arrancar."""
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Database connection verified")


def close_db() -> None:
    """Cierra la conexión a la base de datos."""
    engine.dispose()
