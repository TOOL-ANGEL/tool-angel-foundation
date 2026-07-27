"""
AngelOS Command Base.
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Base class for every AngelOS command.
    """

    name = ""

    description = ""

    @abstractmethod
    def execute(self, **kwargs):
        """
        Execute the command.
        """
        raise NotImplementedError