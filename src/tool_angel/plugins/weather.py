"""
AngelOS Weather Plugin.
"""

from tool_angel.plugins.base import BasePlugin


class WeatherPlugin(BasePlugin):
    """
    Built-in Weather Plugin.
    """

    name = "weather"
    version = "0.1.0"
    author = "AngelOS"
    description = "Built-in weather plugin."