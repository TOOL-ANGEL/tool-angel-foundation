from tool_angel.plugin_loader.plugin_loader import PluginLoader


def test_plugin_loader_loads_weather_plugin():
    loader = PluginLoader()

    manager = loader.load()

    assert manager.get("weather") is not None


def test_plugin_loader_uses_weather_manifest():
    loader = PluginLoader()

    manager = loader.load()

    plugin = manager.get("weather")

    assert plugin is not None
    assert plugin.name == "weather"
    assert plugin.version == "0.1.0"


def test_plugin_loader_registers_plugin_instance():
    loader = PluginLoader()

    manager = loader.load()

    plugin = manager.get("weather")

    assert plugin is not None
    assert plugin.__class__.__name__ == "WeatherPlugin"


def test_plugin_loader_returns_plugin_manager():
    loader = PluginLoader()

    manager = loader.load()

    assert manager is loader.manager
