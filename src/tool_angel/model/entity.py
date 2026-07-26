"""
Golden Component GC-01

Entity
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass(slots=True)
class Entity:
    """
    Fundamental engineering object.

    Every object inside TOOL-ANGEL derives from Entity.
    """

    id: UUID
    name: str
    description: Optional[str] = None

    @classmethod
    def create(cls, name: str, description: Optional[str] = None):
        return cls(
            id=uuid4(),
            name=name,
            description=description,
        )
