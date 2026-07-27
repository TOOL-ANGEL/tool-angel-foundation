"""
AngelOS Runtime Engine.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.runtime.executor import RuntimeExecutor

from tool_angel.plugin_kernel.kernel import PluginKernel

from tool_angel.commands.registry import CommandRegistry
from tool_angel.commands.discovery import CommandDiscovery
from tool_angel.commands.dispatcher import CommandDispatcher

from tool_angel.builtin_commands.plugin import PluginCommand


class RuntimeEngine:
    """Runtime Engine."""

    def __init__(self):

        # Herramientas / Plugins
        self.registry = ToolRegistry()
        self.executor = RuntimeExecutor(self.registry)
        self.kernel = PluginKernel()

        # Comandos
        self.command_registry = CommandRegistry()
        self.command_dispatcher = CommandDispatcher(
            self.command_registry
        )

    def register(self, tool):
        """Register a plugin."""
        self.registry.register(tool)

    def load_tools(self):
        """Load plugins."""

        manager = self.kernel.load()

        for plugin_name in manager.list():

            plugin = manager.get(plugin_name)

            self.register(plugin)

    def load_commands(self):
        """Load built-in commands."""

        # Registrar comandos descubiertos automáticamente
        commands = CommandDiscovery().discover()

        for command in commands:

            self.command_registry.register(command)

        # Registrar PluginCommand
        self.command_registry.register(
            PluginCommand(self)
        )

    def execute_command(self, command_name: str, **kwargs):
        """Execute a command."""

        return self.command_dispatcher.dispatch(
            command_name,
            **kwargs
        )

    def execute(self, tool_name: str, **kwargs):
        """Execute a plugin."""

        return self.executor.execute(
            tool_name,
            **kwargs
        )