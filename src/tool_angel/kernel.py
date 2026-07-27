"""
AngelOS Kernel.
"""

from tool_angel.runtime.engine import RuntimeEngine


class Kernel:
    """AngelOS execution kernel."""

    def __init__(self):
        self.runtime = RuntimeEngine()
        self.started = False

    def start(self):
        """Start the kernel."""
        self.started = True
        print("AngelOS Kernel started.")

    def stop(self):
        """Stop the kernel."""
        self.started = False
        print("AngelOS Kernel stopped.")

    def register(self, tool):
        """Register a tool in the runtime."""
        self.runtime.register(tool)

    def execute(self, tool_name: str, **kwargs):
        """Execute a tool."""
        return self.runtime.execute(tool_name, **kwargs)