class ParsingError(BaseException):
    """Raise when parsing couldn't be completed"""


class SolvingError(BaseException):
    """Raise when solving couldn't be completed"""


class TokenError(BaseException):
    """Raise when Token errors are detected."""


class RuleError(BaseException):
    """Raise when Rule errors are detected."""


class RepoError(BaseException):
    """Raise when Repo errors are detected."""
