"""
Plugin Loader for AngelOS.
"""

import importlib
import pkgutil

from tool_angel.plugins.base import BasePlugin
from tool_angel.plugins.manager import PluginManager


class PluginLoader:
    """Automatically load plugins."""

    def __init__(self, manager: PluginManager) -> None:
        self.manager = manager

    def load(self) -> None:
        """Discover and register available plugins."""

        from tool_angel import plugins

        for _, module_name, _ in pkgutil.iter_modules(plugins.__path__):
            if module_name in (
                "base",
                "manager",
                "__init__",
            ):
                continue

            module = importlib.import_module(f"tool_angel.plugins.{module_name}")

            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and issubclass(obj, BasePlugin)
                    and obj is not BasePlugin
                ):
                    self.manager.register(obj())
