"""
AngelOS Plugin Loader.
"""

from tool_angel.plugin_loader.plugin_discovery import PluginDiscovery
from tool_angel.plugin_loader.manifest_discovery import ManifestDiscovery
from tool_angel.plugin_loader.factory import PluginFactory

from tool_angel.manifest.loader import ManifestLoader
from tool_angel.manifest.parser import ManifestParser
from tool_angel.manifest.validator import ManifestValidator

from tool_angel.plugins.manager import PluginManager


class PluginLoader:
    """
    Loads installed plugins.
    """

    def __init__(self):
        # Descubrimiento de plugins
        self.discovery = PluginDiscovery()

        # Descubrimiento de archivos manifest.yaml
        self.manifest_discovery = ManifestDiscovery()

        # Lectura del contenido YAML
        self.manifest_loader = ManifestLoader()

        # Conversión dict -> ToolManifest
        self.manifest_parser = ManifestParser()

        # Validación del manifiesto
        self.manifest_validator = ManifestValidator()

        # Creación dinámica de plugins
        self.factory = PluginFactory()

        # Registro de plugins cargados
        self.manager = PluginManager()

    def load(self):
        """
        Load installed plugins.
        """

        # 1. Buscar directorios de plugins
        plugin_directories = self.discovery.discover()

        # 2. Buscar archivos manifest.yaml
        manifest_files = self.manifest_discovery.discover(
            plugin_directories
        )

        print(f"Plugin directories: {len(plugin_directories)}")
        print(f"Manifest files: {len(manifest_files)}")

        # 3. Procesar cada manifest encontrado
        for manifest_file in manifest_files:

            # Leer manifest.yaml
            manifest_data = self.manifest_loader.load(
                manifest_file
            )

            # Convertir dict -> ToolManifest
            manifest = self.manifest_parser.parse(
                manifest_data
            )

            # Validar el manifiesto
            if not self.manifest_validator.validate(
                manifest
            ):
                print(
                    f"Invalid manifest: {manifest_file}"
                )
                continue

            # Crear instancia del plugin
            plugin = self.factory.create(
                manifest.entry
            )

            # Registrar plugin
            self.manager.register(plugin)

            print(
                f"Loaded plugin: {manifest.name} ({manifest.version})"
            )

        return self.manager