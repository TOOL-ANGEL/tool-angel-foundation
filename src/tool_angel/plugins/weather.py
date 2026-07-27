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

    def execute(self, *args, **kwargs):
        """
        Execute the Weather plugin.
        """

        print("Weather Plugin")

        if args:
            print("Arguments:")
            print(f" - args: {list(args)}")

        if kwargs:
            print("Options:")
            for key, value in kwargs.items():
                print(f" - {key}: {value}")

        return {
            "plugin": self.name,
            "status": "ok"
        }