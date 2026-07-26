"""
Standard response object for AngelOS SDK.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Response:
    """Standard response returned by every Tool."""

    success: bool
    data: Any = None
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)