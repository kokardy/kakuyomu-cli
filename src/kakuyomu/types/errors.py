"""Custom errors for the project"""


class TOMLAlreadyExists(Exception):
    """TOML already exists"""


class NotLoginError(Exception):
    """Not Login"""


class WorkNotSetError(Exception):
    """Work not set"""
