"""
AngelOS Kernel
"""

from tool_angel.config import Config
from tool_angel.registry import Registry


class Kernel:
    """Main AngelOS kernel."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.registry = Registry()

    def start(self) -> None:
        """Start the kernel."""
        print("AngelOS Kernel started.")

    def stop(self) -> None:
        """Stop the kernel."""
        print("AngelOS Kernel stopped.")