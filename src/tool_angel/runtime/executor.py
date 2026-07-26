"""
AngelOS Runtime Executor.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.sdk.response import Response


class RuntimeExecutor:
    """Executes registered tools."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, **kwargs) -> Response:
        tool = self.registry.get(tool_name)

        if tool is None:
            return Response(
                success=False,
                message=f"Tool '{tool_name}' not found."
            )

        return tool.execute(**kwargs)