"""
AngelOS Runtime Engine.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.runtime.executor import RuntimeExecutor
from tool_angel.loaders.tool_loader import ToolLoader


class RuntimeEngine:
    """Runtime Engine."""

    def __init__(self):

        self.registry = ToolRegistry()

        self.executor = RuntimeExecutor(self.registry)

        self.loader = ToolLoader()

    def register(self, tool):

        self.registry.register(tool)

    def load_tools(self):
        """Automatically load all SDK tools."""

        for tool in self.loader.discover():

            self.register(tool)

    def execute(self, tool_name: str, **kwargs):

        return self.executor.execute(tool_name, **kwargs)