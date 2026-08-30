from tool_angel.plugins.manager import PluginManager
from tool_angel.plugins.weather import WeatherPlugin


def test_plugin_manager_register_and_get():
    manager = PluginManager()
    plugin = WeatherPlugin()

    manager.register(plugin)

    assert manager.get("weather") is plugin


def test_plugin_manager_list_returns_sorted_plugin_names():
    manager = PluginManager()

    plugin_a = WeatherPlugin()
    plugin_a.name = "zeta"

    plugin_b = WeatherPlugin()
    plugin_b.name = "alpha"

    manager.register(plugin_a)
    manager.register(plugin_b)

    assert manager.list() == ["alpha", "zeta"]


def test_plugin_manager_remove():
    manager = PluginManager()
    plugin = WeatherPlugin()

    manager.register(plugin)

    assert manager.get("weather") is plugin

    manager.remove("weather")

    assert manager.get("weather") is None
    assert manager.list() == []


def test_plugin_manager_remove_missing_plugin_is_safe():
    manager = PluginManager()

    manager.remove("does_not_exist")

    assert manager.list() == []


def test_plugin_manager_clear():
    manager = PluginManager()

    manager.register(WeatherPlugin())

    plugin = WeatherPlugin()
    plugin.name = "another"
    manager.register(plugin)

    assert manager.list() == ["another", "weather"]

    manager.clear()

    assert manager.list() == []


def test_plugin_manager_replaces_plugin_with_same_name():
    manager = PluginManager()

    first = WeatherPlugin()
    second = WeatherPlugin()

    manager.register(first)
    manager.register(second)

    assert manager.get("weather") is second
    assert manager.list() == ["weather"]
