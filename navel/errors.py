class NavelError(Exception):
    pass


class ParsingError(NavelError):
    pass


class LinterError(NavelError):
    pass


class ExprError(NavelError):
    pass
