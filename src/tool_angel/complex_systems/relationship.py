"""
AngelOS Complex Systems.

Relationship model between entities inside a complex system.
"""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(slots=True)
class Relationship:
    """
    Represents a relationship between two entities.
    """

    id: UUID
    source_id: UUID
    target_id: UUID
    relationship_type: str
    weight: float = 1.0

    @classmethod
    def create(
        cls,
        source_id: UUID,
        target_id: UUID,
        relationship_type: str,
        weight: float = 1.0,
    ) -> "Relationship":
        """
        Create a relationship between two entities.
        """

        return cls(
            id=uuid4(),
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
        )
