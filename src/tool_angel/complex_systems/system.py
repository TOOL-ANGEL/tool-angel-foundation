"""
AngelOS Complex Systems.

Core model for representing complex systems,
their components, relationships, states and indicators,
and the actors and value functions used by the ecosystem analysis engine.
"""

from typing import Any
from uuid import UUID

from tool_angel.complex_systems.actor import Actor
from tool_angel.complex_systems.component import Component
from tool_angel.complex_systems.indicator import Indicator
from tool_angel.complex_systems.relationship import Relationship
from tool_angel.complex_systems.state import SystemState
from tool_angel.complex_systems.value_function import ValueFunction

DEPENDENCY_TYPES: frozenset[str] = frozenset({"depends_on"})

WEIGHT_TOLERANCE = 1e-9


class ComplexSystem:
    """
    Represents a complex system.

    A complex system is modeled through:

    - Components
    - Relationships
    - States
    - Indicators
    - Actors (who decides over each component)
    - Value functions (what the system delivers and through which path)
    """

    def __init__(
        self,
        name: str,
        description: str = "",
    ) -> None:
        """
        Create a complex system.

        Args:
            name: Name of the system.
            description: Description of the system.
        """

        if not isinstance(name, str) or not name.strip():
            raise ValueError("name cannot be empty")

        self.name = name
        self.description = description

        self.components: list[Component] = []
        self.relationships: list[Relationship] = []
        self.states: list[SystemState] = []
        self.indicators: list[Indicator] = []
        self.actors: list[Actor] = []
        self.value_functions: list[ValueFunction] = []

    # -------------------------------------------------
    # Registration
    # -------------------------------------------------

    @staticmethod
    def _require(item: Any, expected: type, label: str) -> None:
        if not isinstance(item, expected):
            raise TypeError(
                f"{label} must be a {expected.__name__} instance, "
                f"got {type(item).__name__}"
            )

    def add_component(self, component: Component) -> None:
        """
        Add a component to the system.
        """

        self._require(component, Component, "component")
        self.components.append(component)

    def add_relationship(self, relationship: Relationship) -> None:
        """
        Add a relationship to the system.
        """

        self._require(relationship, Relationship, "relationship")
        self.relationships.append(relationship)

    def add_state(self, state: SystemState) -> None:
        """
        Add a state to the system.
        """

        self._require(state, SystemState, "state")
        self.states.append(state)

    def add_indicator(self, indicator: Indicator) -> None:
        """
        Add an indicator to the system.
        """

        self._require(indicator, Indicator, "indicator")
        self.indicators.append(indicator)

    def add_actor(self, actor: Actor) -> None:
        """
        Add an actor to the system.
        """

        self._require(actor, Actor, "actor")
        self.actors.append(actor)

    def add_value_function(self, value_function: ValueFunction) -> None:
        """
        Add a value function to the system.
        """

        self._require(value_function, ValueFunction, "value_function")
        self.value_functions.append(value_function)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    def component_ids(self) -> list[UUID]:
        """Component ids in registration order."""

        return [component.id for component in self.components]

    def component_map(self) -> dict[UUID, Component]:
        """Components indexed by id."""

        return {component.id: component for component in self.components}

    def external_components(self) -> list[Component]:
        """Components owned by third parties (V_ext)."""

        return [component for component in self.components if component.is_external]

    def dependencies(self) -> list[Relationship]:
        """Relationships that represent dependencies (the set E)."""

        return [
            relationship
            for relationship in self.relationships
            if relationship.relationship_type in DEPENDENCY_TYPES
        ]

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    def validation_errors(self) -> list[str]:
        """
        Return every inconsistency that prevents an ecosystem analysis.
        """

        errors: list[str] = []
        components = self.component_map()
        actor_ids = {actor.id for actor in self.actors}

        if len(components) != len(self.components):
            errors.append("component ids must be unique")

        for relationship in self.dependencies():
            for end in (relationship.source_id, relationship.target_id):
                if end not in components:
                    errors.append(
                        f"dependency {relationship.id} references unknown component {end}"
                    )
            if relationship.weight < 0:
                errors.append(f"dependency {relationship.id} has negative weight")

        for component in self.components:
            if (
                component.owner_id is not None
                and actor_ids
                and component.owner_id not in actor_ids
            ):
                errors.append(f"component {component.name!r} has an unknown owner")

        if self.value_functions:
            total = sum(function.weight for function in self.value_functions)
            if abs(total - 1.0) > WEIGHT_TOLERANCE:
                errors.append(f"value function weights must sum to 1, got {total}")
            for function in self.value_functions:
                for member in function.members():
                    if member not in components:
                        errors.append(
                            f"value function {function.name!r} references unknown component {member}"
                        )

        return errors

    def validate(self) -> None:
        """
        Raise ValueError if the system cannot be analyzed.
        """

        errors = self.validation_errors()
        if errors:
            raise ValueError("; ".join(errors))

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """
        Return a summary of the complex system.
        """

        return {
            "name": self.name,
            "description": self.description,
            "components": len(self.components),
            "relationships": len(self.relationships),
            "states": len(self.states),
            "indicators": len(self.indicators),
            "actors": len(self.actors),
            "value_functions": len(self.value_functions),
        }
