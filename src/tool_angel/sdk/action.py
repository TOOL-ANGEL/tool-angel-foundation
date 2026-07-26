"""
AngelOS SDK Action.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Action:
    """
    Represents a callable action of a Tool.
    """

    name: str

    description: str = ""

    parameters: dict[str, Any] = field(default_factory=dict)