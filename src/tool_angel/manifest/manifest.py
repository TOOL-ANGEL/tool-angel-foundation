"""
Tool Manifest definition.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolManifest:
    """Describes a Tool."""

    name: str

    version: str = "1.0.0"

    description: str = ""

    author: str = ""

    actions: list = field(default_factory=list)

    capabilities: list = field(default_factory=list)