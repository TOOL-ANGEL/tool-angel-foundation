"""
Weather Tool Example.
"""

from tool_angel.sdk.action import Action
from tool_angel.sdk.capability import Capability
from tool_angel.sdk.response import Response
from tool_angel.sdk.tool import Tool


class WeatherTool(Tool):

    name = "weather"

    version = "0.1.0"

    description = "Weather information tool."

    capabilities = [
        Capability(
            name="weather.current",
            description="Current weather"
        )
    ]

    actions = [
        Action(
            name="current",
            description="Current weather"
        )
    ]

    def execute(self, **kwargs):

        return Response(
            success=True,
            data={
                "city": kwargs.get("city"),
                "temperature": 24,
                "condition": "Sunny"
            }
        )