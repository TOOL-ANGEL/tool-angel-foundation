"""
AngelOS Command Registry.
"""

from tool_angel.commands.command import Command


class CommandRegistry:
    """
    Registry for AngelOS commands.
    """

    def __init__(self):
        self._commands = {}

    def register(self, command: Command):
        self._commands[command.name] = command

    def get(self, name: str):
        return self._commands.get(name)

    def list(self):
        return sorted(self._commands.keys())

    def remove(self, name: str):
        if name in self._commands:
            del self._commands[name]

    def clear(self):
        self._commands.clear()