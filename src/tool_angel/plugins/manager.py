"""
AngelOS Plugin Manager.
"""

from tool_angel.plugins.base import BasePlugin


class PluginManager:

    def __init__(self):

        self._plugins = {}

    def register(self, plugin: BasePlugin):

        self._plugins[plugin.name] = plugin

    def get(self, name: str):

        return self._plugins.get(name)

    def list(self):

        return sorted(self._plugins.keys())

    def remove(self, name: str):

        if name in self._plugins:
            del self._plugins[name]

    def clear(self):

        self._plugins.clear()