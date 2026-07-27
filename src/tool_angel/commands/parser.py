"""
AngelOS Command Parser.
"""


class CommandParser:
    """
    Parses command line input.
    """

    def parse(self, text: str):

        tokens = text.strip().split()

        if not tokens:
            return None, []

        command = tokens[0]

        args = tokens[1:]

        return command, args