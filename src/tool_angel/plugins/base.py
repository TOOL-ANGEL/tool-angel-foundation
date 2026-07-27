"""
AngelOS Plugin Base.
"""

from abc import ABC


class BasePlugin(ABC):
    """
    Base class for every AngelOS plugin.
    """

    name = ""
    version = "0.1.0"
    author = ""
    description = ""
    enabled = True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def is_enabled(self):
        return self.enabled