"""
AngelOS Complex Systems.

Core model for representing complex systems,
their components, relationships, states and indicators.
"""

from typing import Any


class ComplexSystem:
    """
    Represents a complex system.

    A complex system is modeled through:

    - Components
    - Relationships
    - States
    - Indicators
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

        self.name = name
        self.description = description

        self.components: list[Any] = []
        self.relationships: list[Any] = []
        self.states: list[Any] = []
        self.indicators: list[Any] = []

    # -------------------------------------------------
    # Components
    # -------------------------------------------------

    def add_component(self, component: Any) -> None:
        """
        Add a component to the system.
        """

        self.components.append(component)

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------

    def add_relationship(self, relationship: Any) -> None:
        """
        Add a relationship to the system.
        """

        self.relationships.append(relationship)

    # -------------------------------------------------
    # States
    # -------------------------------------------------

    def add_state(self, state: Any) -> None:
        """
        Add a state to the system.
        """

        self.states.append(state)

    # -------------------------------------------------
    # Indicators
    # -------------------------------------------------

    def add_indicator(self, indicator: Any) -> None:
        """
        Add an indicator to the system.
        """

        self.indicators.append(indicator)

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
        }
