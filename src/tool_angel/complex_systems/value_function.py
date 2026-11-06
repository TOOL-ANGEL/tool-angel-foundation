"""
AngelOS Complex Systems.

Value function model: a business or public function the system delivers,
with its share φ of the total value and its critical path (the set F of the
ecosystem model).

A critical path is a sequence of elements. Each element is either a single
component id (serial: the function fails if it fails) or a tuple of component
ids (a redundant group: the function fails only if all of them fail).
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

PathElement = UUID | tuple[UUID, ...]


@dataclass(slots=True)
class ValueFunction:
    """
    Represents a value function of a complex system.
    """

    id: UUID
    name: str
    weight: float
    path: list[PathElement]
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name cannot be empty")
        if self.weight < 0.0:
            raise ValueError(f"weight must be >= 0, got {self.weight}")
        if not self.path:
            raise ValueError("path cannot be empty")
        for element in self.path:
            if isinstance(element, tuple):
                if len(element) < 2:
                    raise ValueError("a redundant group needs at least two components")
                if not all(isinstance(item, UUID) for item in element):
                    raise TypeError("redundant group elements must be UUIDs")
            elif not isinstance(element, UUID):
                raise TypeError("path elements must be UUIDs or tuples of UUIDs")

    def members(self) -> set[UUID]:
        """All component ids on the critical path, serial or redundant."""

        result: set[UUID] = set()
        for element in self.path:
            if isinstance(element, tuple):
                result.update(element)
            else:
                result.add(element)
        return result

    @classmethod
    def create(
        cls,
        name: str,
        weight: float,
        path: list[PathElement],
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "ValueFunction":
        """
        Create a value function.
        """

        return cls(
            id=uuid4(),
            name=name,
            weight=weight,
            path=list(path),
            description=description,
            metadata=metadata or {},
        )
