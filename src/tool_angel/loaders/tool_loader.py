"""
Automatic Tool Loader.
"""

from pathlib import Path
import importlib
import inspect

from tool_angel.sdk.tool import Tool


class ToolLoader:
    """Automatically discovers Tool subclasses."""

    def __init__(self, package: str = "tool_angel.sdk"):
        self.package = package

    def discover(self):
        """Return instantiated Tool objects."""

        tools = []

        package = importlib.import_module(self.package)

        package_path = Path(package.__file__).parent

        for file in package_path.glob("*_tool.py"):

            module_name = f"{self.package}.{file.stem}"

            module = importlib.import_module(module_name)

            for _, obj in inspect.getmembers(module, inspect.isclass):

                if issubclass(obj, Tool) and obj is not Tool:

                    tools.append(obj())

        return tools