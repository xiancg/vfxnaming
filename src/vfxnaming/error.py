# coding=utf-8


class ParsingError(BaseException):
    '''Raise when parsing couldn't be completed'''


class SolvingError(BaseException):
    '''Raise when solving couldn't be completed'''


class TokenError(BaseException):
    '''Raise when Token errors are detected.'''
