from tool_angel.runtime.engine import RuntimeEngine
from tool_angel.sdk.response import Response


def test_runtime_engine_loads_plugins():
    engine = RuntimeEngine()

    engine.load_tools()

    assert "weather" in engine.registry.list()


def test_runtime_engine_executes_plugin():
    engine = RuntimeEngine()

    engine.load_tools()

    result = engine.execute("weather", city="Bogotá")

    assert isinstance(result, Response)
    assert result.success is True
    assert result.data["plugin"] == "weather"
    assert result.data["status"] == "ok"


def test_runtime_engine_missing_plugin():
    engine = RuntimeEngine()

    result = engine.execute("plugin_that_does_not_exist")

    assert isinstance(result, Response)
    assert result.success is False
    assert "not found" in result.message.lower()
