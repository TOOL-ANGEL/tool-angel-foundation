"""
AngelOS Plugin Command.
"""

from tool_angel.commands.command import Command


class PluginCommand(Command):
    """
    Executes installed plugins.
    """

    name = "plugin"

    description = "Execute an installed plugin."

    def __init__(self, runtime):
        self.runtime = runtime

    def execute(self, *args, **kwargs):
        """
        Execute a plugin.

        Usage:

            plugin weather
            plugin weather current Medellín
        """

        if not args:
            print("Plugin name required.")
            return

        plugin_name = args[0]

        plugin_args = args[1:]

        print(f"Executing plugin: {plugin_name}")

        if plugin_args:
            print("Arguments:")

            for arg in plugin_args:
                print(f" - {arg}")

        if kwargs:
            print("Options:")

            for key, value in kwargs.items():
                print(f" - {key}: {value}")

        return self.runtime.execute(
            plugin_name,
            *plugin_args,
            **kwargs
        )