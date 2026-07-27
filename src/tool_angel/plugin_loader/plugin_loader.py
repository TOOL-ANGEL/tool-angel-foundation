"""
Plugin Loader.
"""

from tool_angel.plugin_loader.plugin_discovery import PluginDiscovery
from tool_angel.plugins.manager import PluginManager


class PluginLoader:

    def __init__(self):

        self.discovery = PluginDiscovery()

        self.manager = PluginManager()

    def load(self):

        plugins = self.discovery.discover()

        for plugin in plugins:
            self.manager.register(plugin)

        return self.manager