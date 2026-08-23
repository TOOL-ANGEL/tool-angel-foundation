"""
Golden Component GC-01

Entity
"""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(slots=True)
class Entity:
    """
    Fundamental engineering object.

    Every object inside TOOL-ANGEL derives from Entity.
    """

    id: UUID
    name: str
    description: str | None = None

    def update_name(self, name: str) -> None:
        """Update the entity name."""
        self.name = name

    @classmethod
    def create(
        cls,
        name: str,
        description: str | None = None,
    ) -> "Entity":
        """
        Create a new Entity.

        Args:
            name: Name of the entity.
            description: Optional description of the entity.

        Returns:
            A new Entity instance.
        """
        return cls(
            id=uuid4(),
            name=name,
            description=description,
        )
