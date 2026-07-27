"""
AngelOS Tool Manifest.
"""

from dataclasses import dataclass, field
from typing import List


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

    permissions: List[str] = field(default_factory=list)

    commands: List[str] = field(default_factory=list)