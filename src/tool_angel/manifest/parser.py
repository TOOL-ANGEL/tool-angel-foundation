"""
AngelOS Manifest Parser.
"""

from tool_angel.manifest.manifest import ToolManifest


class ManifestParser:
    """
    Parses manifest dictionaries into ToolManifest objects.
    """

    def parse(
        self,
        data: dict,
    ) -> ToolManifest:
        """
        Convert a dictionary into a ToolManifest.
        """

        return ToolManifest(
            name=data.get("name", ""),
            version=data.get("version", ""),
            author=data.get("author", ""),
            description=data.get("description", ""),
            entry=data.get("entry", ""),
            permissions=data.get("permissions", []),
            commands=data.get("commands", []),
        )