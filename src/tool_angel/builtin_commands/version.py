"""
AngelOS Version Command.
"""

from tool_angel.commands.command import Command


class VersionCommand(Command):
    """
    Displays AngelOS version.
    """

    name = "version"

    description = "Show AngelOS version."

    def execute(self, **kwargs):

        print("AngelOS version 0.1.0")