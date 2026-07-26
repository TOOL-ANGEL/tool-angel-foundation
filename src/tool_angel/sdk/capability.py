"""
Capability definition for AngelOS SDK.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    """Represents a capability provided by a Tool."""

    name: str
    description: str = ""