"""
AngelOS CLI Entry Point.
"""

import sys

from tool_angel.cli.app import CLIApplication


def main():
    app = CLIApplication()

    # Sin argumentos -> mostrar información de la CLI
    if len(sys.argv) <= 1:
        app.run()
        return

    command = sys.argv[1]

    # Comando: plugin
    if command == "plugin":

        if len(sys.argv) < 3:
            app.engine.execute_command("plugin")
            return

        plugin_name = sys.argv[2]

        plugin_args = sys.argv[3:]

        app.engine.execute_command(
            "plugin",
            plugin_name,
            *plugin_args
        )

        return

    # Resto de comandos
    app.engine.execute_command(command)


if __name__ == "__main__":
    main()