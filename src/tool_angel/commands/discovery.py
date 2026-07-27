"""
AngelOS Command Discovery.
"""

from tool_angel.builtin_commands.help import HelpCommand
from tool_angel.builtin_commands.version import VersionCommand


class CommandDiscovery:
    """
    Discover built-in commands.
    """

    def discover(self):

        return [

            HelpCommand(),

            VersionCommand(),

        ]