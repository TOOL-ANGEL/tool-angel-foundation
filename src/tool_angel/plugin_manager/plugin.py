"""
Plugin model for AngelOS.
"""


class Plugin:

    def __init__(
        self,
        name: str,
        version: str,
        author: str,
        description: str = "",
        enabled: bool = True,
    ):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.enabled = enabled

    def __repr__(self):

        return (
            f"Plugin("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"enabled={self.enabled})"
        )