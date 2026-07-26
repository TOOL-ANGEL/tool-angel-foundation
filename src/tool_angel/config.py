"""
AngelOS Configuration
"""

from dataclasses import dataclass


@dataclass
class Config:
    """Kernel configuration."""

    debug: bool = False
    verbose: bool = False
    plugin_path: str = "plugins"
    data_path: str = "data"
    cache_path: str = ".cache"