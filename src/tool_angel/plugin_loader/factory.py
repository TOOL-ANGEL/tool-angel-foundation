"""
AngelOS Plugin Factory.
"""

import importlib


class PluginFactory:
    """
    Creates plugin instances from manifest entries.
    """

    def create(self, entry: str):
        """
        Create a plugin instance.

        entry example:

        tool_angel.plugins.weather:WeatherPlugin
        """

        module_name, class_name = entry.split(":")

        module = importlib.import_module(module_name)

        plugin_class = getattr(module, class_name)

        return plugin_class()