"""
AngelOS Plugin Discovery.
"""

from pathlib import Path


class PluginDiscovery:
    """
    Discovers installed plugins.
    """

    def __init__(self):

        self.plugins_path = (
            Path(__file__)
            .parent.parent
            / "plugins"
        )

    def discover(self):
        """
        Discover plugin directories.

        Placeholder implementation.
        """

        plugins = []

        for directory in self.plugins_path.iterdir():

            if directory.is_dir():

                plugins.append(directory)

        return plugins