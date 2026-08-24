"""
AngelOS Complex Systems.

State model for representing the state of a complex system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True)
class SystemState:
    """
    Represents a state of a complex system.
    """

    id: UUID
    name: str
    value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        value: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> "SystemState":
        """
        Create a system state.
        """

        return cls(
            id=uuid4(),
            name=name,
            value=value,
            metadata=metadata or {},
        )
