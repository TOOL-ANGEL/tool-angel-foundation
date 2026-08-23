"""
AngelOS Complex Systems.

State model for representing the state of a complex system.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class SystemState:
    """
    Represents a state of a complex system.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    value: Any = None

    @classmethod
    def create(
        cls,
        name: str,
        value: Any = None,
    ) -> "SystemState":
        """
        Create a system state.
        """

        return cls(
            id=uuid4(),
            name=name,
            value=value,
        )
