"""
AngelOS built-in command discovery.

Lives in builtin_commands so that the generic commands package never imports
concrete commands (removes the commands <-> builtin_commands cycle).
"""

from tool_angel.builtin_commands.ecosystem import EcosystemCommand
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
            EcosystemCommand(),
        ]
