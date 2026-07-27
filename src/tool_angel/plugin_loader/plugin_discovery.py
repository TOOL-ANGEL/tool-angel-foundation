"""
Plugin Discovery.
"""

from tool_angel.plugins.weather import WeatherPlugin


class PluginDiscovery:
    """
    Discover installed plugins.
    """

    def discover(self):
        return [
            WeatherPlugin()
        ]