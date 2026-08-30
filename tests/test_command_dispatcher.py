import pytest

from tool_angel.commands.dispatcher import CommandDispatcher
from tool_angel.commands.registry import CommandRegistry
from tool_angel.sdk.response import Response


class DummyCommand:
    name = "dummy"

    def execute(self, *args, **kwargs):
        return Response(
            success=True,
            message="dummy executed",
            data={"args": args, "kwargs": kwargs},
        )


def test_dispatcher_executes_registered_command():
    registry = CommandRegistry()
    registry.register(DummyCommand())

    dispatcher = CommandDispatcher(registry)

    result = dispatcher.dispatch(
        "dummy",
        "hello",
        value=42,
    )

    assert isinstance(result, Response)
    assert result.success is True
    assert result.data["args"] == ("hello",)
    assert result.data["kwargs"]["value"] == 42


def test_dispatcher_unknown_command():
    registry = CommandRegistry()
    dispatcher = CommandDispatcher(registry)

    with pytest.raises(ValueError, match="Unknown command"):
        dispatcher.dispatch("does_not_exist")
