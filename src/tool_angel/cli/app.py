"""
AngelOS CLI Application.
"""

from tool_angel.runtime.engine import RuntimeEngine


class CLIApplication:
    """AngelOS Command Line Application."""

    def __init__(self):

        self.engine = RuntimeEngine()

        self.engine.load_tools()

        self.engine.load_commands()

    def run(self, command=None):

        if command is None:

            print("AngelOS CLI")

            print("----------------")

            print("Loaded plugins:")

            print(self.engine.registry.list())

            print()

            print("Loaded commands:")

            print(self.engine.command_registry.list())

            return

        self.engine.execute_command(command)