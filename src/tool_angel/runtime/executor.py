"""
AngelOS Runtime Executor.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.sdk.response import Response


class RuntimeExecutor:
    """
    Executes registered plugins.
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        *args,
        **kwargs
    ) -> Response:
        """
        Execute a registered plugin.
        """

        tool = self.registry.get(tool_name)

        if tool is None:
            return Response(
                success=False,
                message=f"Plugin '{tool_name}' not found."
            )

        return tool.execute(
            *args,
            **kwargs
        )