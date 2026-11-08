import pytest

from tool_angel.exceptions import PluginError
from tool_angel.plugin_loader.factory import PluginFactory
from tool_angel.plugins.weather import WeatherPlugin


def test_plugin_factory_creates_weather_plugin():
    factory = PluginFactory()

    plugin = factory.create(
        "tool_angel.plugins.weather:WeatherPlugin"
    )

    assert isinstance(plugin, WeatherPlugin)
    assert plugin.name == "weather"
    assert plugin.version == "0.1.0"


def test_plugin_factory_rejects_empty_entry():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create("")


def test_plugin_factory_rejects_invalid_entry_format():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create("invalid_entry")


def test_plugin_factory_rejects_entry_without_class():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create("tool_angel.plugins.weather:")


def test_plugin_factory_rejects_entry_without_module():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create(":WeatherPlugin")


def test_plugin_factory_rejects_missing_module():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create(
            "tool_angel.plugins.does_not_exist:WeatherPlugin"
        )


def test_plugin_factory_rejects_missing_class():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create(
            "tool_angel.plugins.weather:DoesNotExist"
        )


def test_plugin_factory_rejects_non_class_entry():
    factory = PluginFactory()

    with pytest.raises(PluginError):
        factory.create(
            "tool_angel.plugins.weather:name"
        )
