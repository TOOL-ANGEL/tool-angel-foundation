from tool_angel.manifest.manifest import ToolManifest
from tool_angel.manifest.validator import ManifestValidator


def test_manifest_validator_accepts_valid_manifest():
    manifest = ToolManifest(
        name="weather",
        version="0.1.0",
        author="AngelOS",
        description="Weather plugin",
        entry="tool_angel.plugins.weather:WeatherPlugin",
    )

    result = ManifestValidator().validate(manifest)

    assert result is True


def test_manifest_validator_rejects_missing_required_value():
    manifest = ToolManifest(
        name="",
        version="0.1.0",
        author="AngelOS",
        description="Weather plugin",
        entry="tool_angel.plugins.weather:WeatherPlugin",
    )

    result = ManifestValidator().validate(manifest)

    assert result is False


def test_manifest_validator_rejects_blank_required_value():
    manifest = ToolManifest(
        name="   ",
        version="0.1.0",
        author="AngelOS",
        description="Weather plugin",
        entry="tool_angel.plugins.weather:WeatherPlugin",
    )

    result = ManifestValidator().validate(manifest)

    assert result is False


def test_manifest_validator_rejects_missing_optional_lists():
    manifest = ToolManifest(
        name="weather",
        version="0.1.0",
        author="AngelOS",
        description="Weather plugin",
        entry="tool_angel.plugins.weather:WeatherPlugin",
        permissions=[],
        commands=[],
    )

    result = ManifestValidator().validate(manifest)

    assert result is True
