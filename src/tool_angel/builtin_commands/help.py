"""
AngelOS Help Command.
"""

from tool_angel.commands.command import Command


class HelpCommand(Command):
    """
    Displays available commands.
    """

    name = "help"

    description = "Show available commands."

    def execute(self, **kwargs):

        print("Available commands:")

        print("- help")

        print("- version")

        print("- plugins")