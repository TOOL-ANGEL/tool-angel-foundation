"""
AngelOS Tool Manifest.
"""

from dataclasses import dataclass, field


@dataclass
class ToolManifest:
    """
    Describes a plugin/tool manifest.
    """

    name: str

    version: str

    author: str

    description: str

    entry: str

    permissions: list[str] = field(default_factory=list)

    commands: list[str] = field(default_factory=list)
