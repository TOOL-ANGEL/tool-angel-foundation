"""
AngelOS Runtime Engine.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.runtime.executor import RuntimeExecutor

from tool_angel.plugin_kernel.kernel import PluginKernel


class RuntimeEngine:
    """Runtime Engine."""

    def __init__(self):

        self.registry = ToolRegistry()

        self.executor = RuntimeExecutor(self.registry)

        self.kernel = PluginKernel()

    def register(self, tool):

        self.registry.register(tool)

    def load_tools(self):
        """Automatically load all SDK tools."""

        manager = self.kernel.load()

        for plugin_name in manager.list():

            plugin = manager.get(plugin_name)

            self.register(plugin)

    def execute(self, tool_name: str, **kwargs):

        return self.executor.execute(tool_name, **kwargs)