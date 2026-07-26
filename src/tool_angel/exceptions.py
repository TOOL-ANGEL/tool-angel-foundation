"""
AngelOS Exceptions
"""


class AngelError(Exception):
    """Base exception for AngelOS."""


class ConfigurationError(AngelError):
    """Invalid configuration."""


class PluginError(AngelError):
    """Plugin loading error."""


class RegistryError(AngelError):
    """Registry error."""


class KernelError(AngelError):
    """Kernel execution error."""


class ValidationError(AngelError):
    """Validation error."""