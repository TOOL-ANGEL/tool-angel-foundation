"""
Base Tool for AngelOS SDK.
"""

from abc import ABC, abstractmethod


class Tool(ABC):
    """Base class for every AngelOS Tool."""

    name: str = "tool"
    version: str = "0.1.0"
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs):
        """Execute the tool."""
        raise NotImplementedError