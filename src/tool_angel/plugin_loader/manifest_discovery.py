"""
AngelOS Manifest Discovery.
"""

from pathlib import Path


class ManifestDiscovery:
    """
    Discovers plugin manifest files.
    """

    def discover(self, plugin_directories):
        """
        Search for manifest.yaml in each plugin directory.
        """

        manifests = []

        for directory in plugin_directories:

            manifest = directory / "manifest.yaml"

            if manifest.exists():

                manifests.append(manifest)

        return manifests