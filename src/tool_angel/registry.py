"""
AngelOS Registry
"""

from typing import Any


class Registry:
    """Simple object registry."""

    def __init__(self) -> None:
        self._items: dict[str, Any] = {}

    def register(self, name: str, obj: Any) -> None:
        """Register an object."""
        self._items[name] = obj

    def get(self, name: str) -> Any:
        """Retrieve an object."""
        return self._items[name]

    def exists(self, name: str) -> bool:
        """Check if object exists."""
        return name in self._items

    def all(self) -> dict[str, Any]:
        """Return all objects."""
        return self._items