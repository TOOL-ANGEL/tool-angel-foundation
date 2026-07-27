"""
Plugin Context.
"""


class PluginContext:
    """
    Shared execution context for plugins.
    """

    def __init__(self):

        self.data = {}

    def set(self, key, value):

        self.data[key] = value

    def get(self, key, default=None):

        return self.data.get(key, default)

    def clear(self):

        self.data.clear()