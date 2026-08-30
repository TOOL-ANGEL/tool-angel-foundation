"""
AngelOS Complex Systems.

Component model for representing components inside a complex system.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class Component:
    """
    Represents a component of a complex system.
    """

    id: UUID
    name: str
    type: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        type: str = "",
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "Component":
        """
        Create a system component.
        """

        return cls(
            id=uuid4(),
            name=name,
            type=type,
            description=description,
            metadata=metadata or {},
        )
