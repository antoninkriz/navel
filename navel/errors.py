"""
Custom errors module
"""


class NavelError(Exception):
    """
    General Navel error
    """


class ParsingError(NavelError):
    """
    Error when parsing Navel config
    """


class LinterError(NavelError):
    """
    Error when linting a file
    """


class ExprError(NavelError):
    """
    Error when an expression is not a valid expression
    """
