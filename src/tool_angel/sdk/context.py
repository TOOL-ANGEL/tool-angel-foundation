"""
Execution Context for AngelOS SDK.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    """Shared execution context."""

    user: str = "anonymous"
    session_id: str = ""
    variables: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)