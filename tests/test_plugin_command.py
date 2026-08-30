from tool_angel.runtime.engine import RuntimeEngine
from tool_angel.sdk.response import Response


def test_plugin_command_is_registered():
    engine = RuntimeEngine()

    engine.load_commands()

    assert "plugin" in engine.command_registry.list()


def test_plugin_command_executes_weather():
    engine = RuntimeEngine()

    engine.load_tools()
    engine.load_commands()

    result = engine.execute_command(
        "plugin",
        "weather",
        city="Bogotá",
    )

    assert isinstance(result, Response)
    assert result.success is True
    assert result.data["plugin"] == "weather"
    assert result.data["status"] == "ok"


def test_plugin_command_missing_plugin():
    engine = RuntimeEngine()

    engine.load_tools()
    engine.load_commands()

    result = engine.execute_command(
        "plugin",
        "plugin_that_does_not_exist",
    )

    assert isinstance(result, Response)
    assert result.success is False
