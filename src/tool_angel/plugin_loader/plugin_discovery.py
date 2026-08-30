"""
AngelOS Plugin Discovery.
"""

from pathlib import Path


class PluginDiscovery:
    """
    Discovers installed plugins.
    """

    def __init__(self):

        self.plugins_path = Path(__file__).parent.parent / "plugins"

    def discover(self):
        """
        Discover plugin directories containing a manifest.yaml file.
        """

        plugins = []

        for directory in self.plugins_path.iterdir():

            if directory.is_dir() and (directory / "manifest.yaml").is_file():

                plugins.append(directory)

        return plugins
