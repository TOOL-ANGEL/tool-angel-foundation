"""
Weather Plugin.
"""

from tool_angel.plugins.base import Plugin


class WeatherPlugin(Plugin):
    """Example weather plugin."""

    name = "weather"

    version = "0.1.0"

    description = "Example weather plugin."

    def run(self) -> None:
        print("Weather plugin executed.")