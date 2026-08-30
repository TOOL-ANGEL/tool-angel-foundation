from tool_angel.runtime.engine import RuntimeEngine
from tool_angel.sdk.response import Response


def test_runtime_engine_loads_commands():
    engine = RuntimeEngine()

    engine.load_commands()

    commands = engine.command_registry.list()

    assert "plugin" in commands


def test_runtime_engine_executes_plugin_command():
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


def test_runtime_engine_command_and_plugin_runtime_work_together():
    engine = RuntimeEngine()

    engine.load_tools()
    engine.load_commands()

    assert "weather" in engine.registry.list()
    assert "plugin" in engine.command_registry.list()

    result = engine.execute_command(
        "plugin",
        "weather",
        city="Bogotá",
    )

    assert result.success is True
