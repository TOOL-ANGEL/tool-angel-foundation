from tool_angel.manifest.manifest import ToolManifest
from tool_angel.manifest.parser import ManifestParser


def test_manifest_parser_creates_tool_manifest():
    data = {
        "name": "weather",
        "version": "0.1.0",
        "author": "AngelOS",
        "description": "Weather plugin",
        "entry": "tool_angel.plugins.weather:WeatherPlugin",
        "permissions": ["network"],
        "commands": ["weather"],
    }

    result = ManifestParser().parse(data)

    assert isinstance(result, ToolManifest)
    assert result.name == "weather"
    assert result.version == "0.1.0"
    assert result.author == "AngelOS"
    assert result.description == "Weather plugin"
    assert result.entry == "tool_angel.plugins.weather:WeatherPlugin"
    assert result.permissions == ["network"]
    assert result.commands == ["weather"]


def test_manifest_parser_uses_defaults_for_optional_fields():
    data = {
        "name": "weather",
        "version": "0.1.0",
        "author": "AngelOS",
        "description": "Weather plugin",
        "entry": "tool_angel.plugins.weather:WeatherPlugin",
    }

    result = ManifestParser().parse(data)

    assert result.permissions == []
    assert result.commands == []


def test_manifest_parser_defaults_missing_required_fields_to_empty_strings():
    result = ManifestParser().parse({})

    assert isinstance(result, ToolManifest)
    assert result.name == ""
    assert result.version == ""
    assert result.author == ""
    assert result.description == ""
    assert result.entry == ""
    assert result.permissions == []
    assert result.commands == []
