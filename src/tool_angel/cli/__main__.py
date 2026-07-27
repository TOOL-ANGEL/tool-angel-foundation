"""
AngelOS CLI Entry Point.
"""

import sys

from tool_angel.cli.app import CLIApplication


def main():
    app = CLIApplication()

    if len(sys.argv) > 1:
        app.run(sys.argv[1])
    else:
        app.run()


if __name__ == "__main__":
    main()