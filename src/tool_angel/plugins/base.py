"""
Base Plugin class for AngelOS.
"""

from abc import ABC, abstractmethod


class Plugin(ABC):
    """Base class for every AngelOS plugin."""

    name: str = "plugin"
    version: str = "0.1.0"
    description: str = ""

    @abstractmethod
    def run(self) -> None:
        """Execute the plugin."""
        raise NotImplementedError