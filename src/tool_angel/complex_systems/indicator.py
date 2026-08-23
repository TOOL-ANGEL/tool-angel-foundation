"""
AngelOS Complex Systems.

Indicator model for measuring complex system behavior.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class Indicator:
    """
    Represents an indicator associated with a complex system.
    """

    id: UUID
    name: str
    value: float | None = None
    unit: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        value: float | None = None,
        unit: str = "",
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "Indicator":
        """
        Create a system indicator.
        """

        return cls(
            id=uuid4(),
            name=name,
            value=value,
            unit=unit,
            description=description,
            metadata=metadata or {},
        )
