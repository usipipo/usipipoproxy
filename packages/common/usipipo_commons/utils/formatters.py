"""Formateadores compartidos."""
from datetime import datetime


def format_bytes(gb: float) -> str:
    """Formatea bytes a GB legible."""
    if gb >= 1000:
        return f"{gb / 1000:.2f} TB"
    return f"{gb:.2f} GB"


def format_datetime(dt: datetime) -> str:
    """Formatea datetime a string legible."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_duration(seconds: int) -> str:
    """Formatea duración en segundos a string legible."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
