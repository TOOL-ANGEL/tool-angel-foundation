from abc import ABC, abstractmethod

from tool_angel.sdk.action import Action
from tool_angel.sdk.capability import Capability


class Tool(ABC):

    name: str = "tool"
    version: str = "0.1.0"
    description: str = ""

    capabilities: list[Capability] = []
    actions: list[Action] = []

    @abstractmethod
    def execute(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def manifest(self):
        raise NotImplementedError