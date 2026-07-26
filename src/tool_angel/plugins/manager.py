"""
Plugin Manager for AngelOS.
"""

from tool_angel.plugins.base import Plugin


class PluginManager:
    """Manage AngelOS plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Plugin | None:
        """Return a plugin by name."""
        return self._plugins.get(name)

    def list(self) -> list[str]:
        """Return all registered plugin names."""
        return sorted(self._plugins.keys())