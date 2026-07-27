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
    """
    AngelOS Runtime Engine.

    Responsible for:

    - Loading plugins
    - Loading commands
    - Executing commands
    - Executing plugins
    """

    def __init__(self):

        # -------------------------------------------------
        # Plugin Runtime
        # -------------------------------------------------

        self.registry = ToolRegistry()

        self.executor = RuntimeExecutor(
            self.registry
        )

        self.kernel = PluginKernel()

        # -------------------------------------------------
        # Command Runtime
        # -------------------------------------------------

        self.command_registry = CommandRegistry()

        self.command_dispatcher = CommandDispatcher(
            self.command_registry
        )

    # -------------------------------------------------
    # Plugins
    # -------------------------------------------------

    def register(self, tool):
        """
        Register a plugin.
        """

        self.registry.register(tool)

    def load_tools(self):
        """
        Automatically load all plugins.
        """

        manager = self.kernel.load()

        for plugin_name in manager.list():

            plugin = manager.get(plugin_name)

            self.register(plugin)

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    def load_commands(self):
        """
        Load all built-in commands.
        """

        commands = CommandDiscovery().discover()

        for command in commands:

            self.command_registry.register(command)

        # Register plugin command

        self.command_registry.register(
            PluginCommand(self)
        )

    # -------------------------------------------------
    # Execute Commands
    # -------------------------------------------------

    def execute_command(
        self,
        command_name: str,
        *args,
        **kwargs
    ):
        """
        Execute a command.
        """

        return self.command_dispatcher.dispatch(
            command_name,
            *args,
            **kwargs
        )

    # -------------------------------------------------
    # Execute Plugins
    # -------------------------------------------------

    def execute(
        self,
        tool_name: str,
        *args,
        **kwargs
    ):
        """
        Execute a plugin.
        """

        return self.executor.execute(
            tool_name,
            *args,
            **kwargs
        )