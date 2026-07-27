"""
AngelOS Manifest Loader.
"""

from pathlib import Path

import yaml


class ManifestLoader:
    """
    Loads manifest.yaml files.
    """

    def load(
        self,
        manifest_path: Path
    ) -> dict:
        """
        Load a manifest.yaml file.

        Returns the raw dictionary.
        """

        with open(
            manifest_path,
            "r",
            encoding="utf-8"
        ) as file:

            return yaml.safe_load(file)