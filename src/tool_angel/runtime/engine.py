"""
AngelOS Runtime Engine.
"""

from tool_angel.runtime.registry import ToolRegistry
from tool_angel.runtime.executor import RuntimeExecutor
from tool_angel.runtime.session import RuntimeSession


class RuntimeEngine:
    """Coordinates runtime execution."""

    def __init__(self):
        self.registry = ToolRegistry()
        self.executor = RuntimeExecutor(self.registry)

    def create_session(self, session_id: str, user: str = "anonymous"):
        return RuntimeSession(
            id=session_id,
            user=user,
        )

    def register(self, tool):
        self.registry.register(tool)

    def execute(self, tool_name: str, **kwargs):
        return self.executor.execute(tool_name, **kwargs)