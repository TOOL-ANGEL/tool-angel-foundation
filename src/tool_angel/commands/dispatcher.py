"""
AngelOS Command Dispatcher.
"""

from tool_angel.commands.registry import CommandRegistry


class CommandDispatcher:
    """
    Dispatches registered commands.
    """

    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def dispatch(
        self,
        command_name: str,
        *args,
        **kwargs
    ):
        """
        Dispatch a command to its implementation.
        """

        command = self.registry.get(command_name)

        if command is None:
            raise ValueError(
                f"Unknown command: {command_name}"
            )

        return command.execute(
            *args,
            **kwargs
        )