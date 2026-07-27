"""
AngelOS Manifest Validator.
"""

from tool_angel.manifest.manifest import ToolManifest


class ManifestValidator:
    """
    Validates plugin manifests.
    """

    REQUIRED_FIELDS = (
        "name",
        "version",
        "author",
        "description",
        "entry",
    )

    def validate(
        self,
        manifest: ToolManifest,
    ) -> bool:
        """
        Validate a ToolManifest instance.
        """

        for field in self.REQUIRED_FIELDS:

            value = getattr(
                manifest,
                field,
                None,
            )

            if value is None:
                return False

            if isinstance(value, str):

                if not value.strip():
                    return False

        return True