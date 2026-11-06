"""
AngelOS Complex Systems.

Actor model: a team, provider or partner with decision power over
components of a complex system (the set A of the ecosystem model).
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class Actor:
    """
    Represents an actor that owns components of a complex system.
    """

    id: UUID
    name: str
    kind: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name cannot be empty")

    @classmethod
    def create(
        cls,
        name: str,
        kind: str = "",
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "Actor":
        """
        Create an actor.
        """

        return cls(
            id=uuid4(),
            name=name,
            kind=kind,
            description=description,
            metadata=metadata or {},
        )
