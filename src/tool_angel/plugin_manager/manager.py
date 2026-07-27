"""
Plugin Manager for AngelOS.
"""

from tool_angel.plugin_manager.plugin import Plugin


class PluginManager:

    def __init__(self):

        self._plugins = {}

    def register(self, plugin: Plugin):

        self._plugins[plugin.name] = plugin

    def get(self, name: str):

        return self._plugins.get(name)

    def list(self):

        return sorted(self._plugins.keys())