"""
Admin Operation Result entity for uSipipo Commons.

This module contains the AdminOperationResult dataclass for administrative operation results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AdminOperationResult:
    """
    Result of an administrative operation.

    This entity represents the outcome of administrative actions
    and provides standardized response formatting.
    """

    success: bool
    operation: str
    target_id: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
