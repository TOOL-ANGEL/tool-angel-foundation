"""
AngelOS Runtime Session.
"""

from dataclasses import dataclass, field


@dataclass
class RuntimeSession:
    """Represents one execution session."""

    id: str
    user: str = "anonymous"
    state: dict = field(default_factory=dict)

    def set(self, key, value):
        self.state[key] = value

    def get(self, key, default=None):
        return self.state.get(key, default)