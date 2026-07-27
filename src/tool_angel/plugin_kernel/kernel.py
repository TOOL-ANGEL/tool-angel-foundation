"""
Plugin Kernel.
"""

from tool_angel.plugin_loader.plugin_loader import PluginLoader
from tool_angel.plugin_kernel.context import PluginContext
from tool_angel.plugin_kernel.lifecycle import PluginLifecycle


class PluginKernel:
    """
    Central plugin kernel.
    """

    def __init__(self):

        self.loader = PluginLoader()

        self.manager = None

        self.context = PluginContext()

        self.lifecycle = PluginLifecycle()

    def load(self):

        self.manager = self.loader.load()

        self.lifecycle.set_state(PluginLifecycle.LOADED)

        return self.manager