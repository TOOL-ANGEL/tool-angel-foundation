"""
AngelOS Weather Plugin.
"""

from tool_angel.plugins.base import BasePlugin
from tool_angel.sdk.response import Response


class WeatherPlugin(BasePlugin):
    """
    Built-in weather plugin.
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

        return Response(
            success=True,
            message="Weather plugin executed successfully.",
            data={
                "plugin": self.name,
                "status": "ok",
            },
        )
