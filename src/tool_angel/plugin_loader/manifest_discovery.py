"""
AngelOS Manifest Discovery.
"""


class ManifestDiscovery:
    """
    Discovers plugin manifest files.
    """

    def discover(self, plugin_directories):
        """
        Search for manifest.yaml files in plugin directories.
        """

        manifests = []

        for directory in plugin_directories:

            manifest = directory / "manifest.yaml"

            if manifest.is_file():

                manifests.append(manifest)

        return manifests
