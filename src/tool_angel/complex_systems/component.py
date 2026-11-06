"""
AngelOS Complex Systems.

Component model for representing components inside a complex system.

Besides its identity, a component carries the parameters the ecosystem
analysis engine needs (CS-02): its scope (internal or external), the actor
that owns it, its availability A, the contractual control γ the system holds
over it, and its yearly rate λ of failures or incompatible changes.
"""

from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import UUID, uuid4

Scope = Literal["internal", "external"]

SCOPES: tuple[str, ...] = ("internal", "external")


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
    scope: Scope = "internal"
    owner_id: UUID | None = None
    availability: float = 1.0
    control: float = 1.0
    failure_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}, got {self.scope!r}")
        for label, value in (
            ("availability", self.availability),
            ("control", self.control),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{label} must lie in [0, 1], got {value}")
        if self.failure_rate < 0.0:
            raise ValueError(f"failure_rate must be >= 0, got {self.failure_rate}")
        if self.scope == "internal" and self.control != 1.0:
            raise ValueError("internal components must have control = 1")

    @property
    def is_external(self) -> bool:
        """True when the component belongs to a third party."""

        return self.scope == "external"

    @classmethod
    def create(
        cls,
        name: str,
        type: str = "",
        description: str = "",
        metadata: dict[str, Any] | None = None,
        *,
        scope: Scope = "internal",
        owner_id: UUID | None = None,
        availability: float = 1.0,
        control: float | None = None,
        failure_rate: float = 0.0,
    ) -> "Component":
        """
        Create a system component.

        When ``control`` is omitted it defaults to 1 for internal components
        and to 0 for external ones.
        """

        if control is None:
            control = 1.0 if scope == "internal" else 0.0

        return cls(
            id=uuid4(),
            name=name,
            type=type,
            description=description,
            metadata=metadata or {},
            scope=scope,
            owner_id=owner_id,
            availability=availability,
            control=control,
            failure_rate=failure_rate,
        )
