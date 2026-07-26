"""
Plugin Loader for AngelOS.
"""

import importlib
import pkgutil

from tool_angel.plugins.base import Plugin
from tool_angel.plugins.manager import PluginManager


class PluginLoader:
    """Automatically load plugins."""

    def __init__(self, manager: PluginManager):
        self.manager = manager

    def load(self):
        import tool_angel.plugins as plugins

        for _, module_name, _ in pkgutil.iter_modules(
            plugins.__path__
        ):

            if module_name in (
                "base",
                "manager",
                "__init__",
            ):
                continue

            module = importlib.import_module(
                f"tool_angel.plugins.{module_name}"
            )

            for obj in module.__dict__.values():

                if (
                    isinstance(obj, type)
                    and issubclass(obj, Plugin)
                    and obj is not Plugin
                ):
                    self.manager.register(obj())