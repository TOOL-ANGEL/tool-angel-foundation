"""
AngelOS Plugin Factory.

Creates plugin instances dynamically from manifest entry points.
"""

import importlib
from typing import Any

from tool_angel.exceptions import PluginError


class PluginFactory:
    """
    Creates plugin instances from manifest entries.

    Expected entry format:

        tool_angel.plugins.weather:WeatherPlugin
    """

    def create(self, entry: str) -> Any:
        """
        Create a plugin instance from its module and class entry.

        Args:
            entry: Import path in module:class format.

        Returns:
            An instance of the requested plugin.

        Raises:
            PluginError: If the entry is invalid or the plugin
                cannot be imported or instantiated.
        """

        if not isinstance(entry, str) or not entry.strip():
            raise PluginError("Plugin entry must be a non-empty string.")

        parts = entry.split(":")

        if len(parts) != 2:
            raise PluginError(
                "Invalid plugin entry format. Expected module:ClassName."
            )

        module_name, class_name = (part.strip() for part in parts)

        if not module_name or not class_name:
            raise PluginError(
                "Plugin entry must contain a module and a class name."
            )

        try:
            module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError) as exc:
            raise PluginError(
                f"Could not import plugin module '{module_name}'."
            ) from exc

        try:
            plugin_class = getattr(module, class_name)
        except AttributeError as exc:
            raise PluginError(
                f"Plugin class '{class_name}' was not found "
                f"in module '{module_name}'."
            ) from exc

        if not isinstance(plugin_class, type):
            raise PluginError(
                f"Plugin entry '{class_name}' is not a class."
            )

        try:
            return plugin_class()
        except Exception as exc:
            raise PluginError(
                f"Could not instantiate plugin '{class_name}'."
            ) from exc
