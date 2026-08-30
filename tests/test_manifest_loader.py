from tool_angel.manifest.loader import ManifestLoader


def test_manifest_loader_reads_yaml_into_dictionary(tmp_path):
    manifest = tmp_path / "manifest.yaml"

    manifest.write_text(
        """
name: weather
version: "0.1.0"
author: AngelOS
description: Weather plugin
entry: tool_angel.plugins.weather:WeatherPlugin
permissions:
  - network
commands:
  - weather
""",
        encoding="utf-8",
    )

    result = ManifestLoader().load(manifest)

    assert result == {
        "name": "weather",
        "version": "0.1.0",
        "author": "AngelOS",
        "description": "Weather plugin",
        "entry": "tool_angel.plugins.weather:WeatherPlugin",
        "permissions": ["network"],
        "commands": ["weather"],
    }


def test_manifest_loader_returns_empty_value_for_empty_yaml(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text("", encoding="utf-8")

    result = ManifestLoader().load(manifest)

    assert result is None
