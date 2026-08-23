"""
AngelOS Complex Systems.

Indicator model for measuring complex systems.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class Indicator:
    """
    Represents an indicator of a complex system.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    value: Any = None
    unit: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        value: Any = None,
        unit: str = "",
    ) -> "Indicator":
        """
        Create a system indicator.
        """

        return cls(
            id=uuid4(),
            name=name,
            value=value,
            unit=unit,
        )
