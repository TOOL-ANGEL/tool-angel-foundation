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
            result = app.engine.execute_command("plugin")
            print(result)
            return

        plugin_name = sys.argv[2]
        plugin_args = sys.argv[3:]

        kwargs = {}
        args = []

        for item in plugin_args:
            if "=" in item:
                key, value = item.split("=", 1)
                kwargs[key] = value
            else:
                args.append(item)

        result = app.engine.execute_command(
            "plugin",
            plugin_name,
            *args,
            **kwargs,
        )

        print(result)
        return

    # Resto de comandos
    result = app.engine.execute_command(command)
    print(result)


if __name__ == "__main__":
    main()
