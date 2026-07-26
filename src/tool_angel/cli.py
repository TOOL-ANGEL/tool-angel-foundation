"""
AngelOS CLI
"""

import argparse

from tool_angel.kernel import Kernel
from tool_angel.version import NAME, __version__


def main() -> None:
    parser = argparse.ArgumentParser(prog="angel")

    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        choices=["start", "stop", "version"],
    )

    args = parser.parse_args()

    kernel = Kernel()

    if args.command == "start":
        kernel.start()

    elif args.command == "stop":
        kernel.stop()

    elif args.command == "version":
        print(f"{NAME} {__version__}")


if __name__ == "__main__":
    main()