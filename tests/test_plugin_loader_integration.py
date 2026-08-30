from tool_angel.plugin_loader.plugin_loader import PluginLoader


def test_plugin_loader_loads_weather_plugin():
    manager = PluginLoader().load()

    assert "weather" in manager.list()

    plugin = manager.get("weather")

    assert plugin is not None
    assert plugin.name == "weather"
    assert plugin.version == "0.1.0"


def test_plugin_loader_returns_registered_plugin_manager():
    manager = PluginLoader().load()

    assert manager.list() == ["weather"]


def test_plugin_loader_weather_plugin_is_executable():
    manager = PluginLoader().load()

    plugin = manager.get("weather")

    assert plugin is not None

    result = plugin.execute(city="Bogotá")

    assert result.success is True
    assert result.data["plugin"] == "weather"
    assert result.data["status"] == "ok"
