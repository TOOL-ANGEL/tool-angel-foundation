from tool_angel.plugin_loader.manifest_discovery import ManifestDiscovery
from tool_angel.plugin_loader.plugin_discovery import PluginDiscovery


def test_plugin_discovery_finds_only_plugin_directories_with_manifest(tmp_path):
    plugins_path = tmp_path / "plugins"
    plugins_path.mkdir()

    weather = plugins_path / "weather"
    weather.mkdir()
    (weather / "manifest.yaml").write_text("name: weather\n")

    empty_plugin = plugins_path / "empty_plugin"
    empty_plugin.mkdir()

    file_entry = plugins_path / "not_a_plugin.txt"
    file_entry.write_text("test")

    discovery = PluginDiscovery()
    discovery.plugins_path = plugins_path

    result = discovery.discover()

    assert result == [weather]


def test_manifest_discovery_finds_manifest_files(tmp_path):
    plugins_path = tmp_path / "plugins"
    plugins_path.mkdir()

    weather = plugins_path / "weather"
    weather.mkdir()

    manifest = weather / "manifest.yaml"
    manifest.write_text("name: weather\n")

    empty_plugin = plugins_path / "empty_plugin"
    empty_plugin.mkdir()

    result = ManifestDiscovery().discover([weather, empty_plugin])

    assert result == [manifest]


def test_manifest_discovery_ignores_directories_without_manifest(tmp_path):
    plugins_path = tmp_path / "plugins"
    plugins_path.mkdir()

    plugin_a = plugins_path / "plugin_a"
    plugin_a.mkdir()

    plugin_b = plugins_path / "plugin_b"
    plugin_b.mkdir()

    result = ManifestDiscovery().discover([plugin_a, plugin_b])

    assert result == []
