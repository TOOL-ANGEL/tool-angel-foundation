from tool_angel.plugin_loader.manifest_discovery import ManifestDiscovery


def test_manifest_discovery_finds_existing_manifest(tmp_path):
    plugin = tmp_path / "weather"
    plugin.mkdir()

    manifest = plugin / "manifest.yaml"
    manifest.write_text("name: weather\n")

    result = ManifestDiscovery().discover([plugin])

    assert result == [manifest]


def test_manifest_discovery_ignores_missing_manifest(tmp_path):
    plugin = tmp_path / "weather"
    plugin.mkdir()

    result = ManifestDiscovery().discover([plugin])

    assert result == []


def test_manifest_discovery_ignores_manifest_directory(tmp_path):
    plugin = tmp_path / "weather"
    plugin.mkdir()

    manifest = plugin / "manifest.yaml"
    manifest.mkdir()

    result = ManifestDiscovery().discover([plugin])

    assert result == []
