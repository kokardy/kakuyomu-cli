"""Custom errors for the project"""


class TOMLAlreadyExistsError(Exception):
    """TOML already exists"""


class NotLoginError(Exception):
    """Not Login"""


class WorkNotSetError(Exception):
    """Work not set"""


class EpisodeAlreadyLinkedError(Exception):
    """Episode already linked"""


class EpisodeNotFoundError(Exception):
    """Episode not found error"""


class EpisodeHasNoPathError(Exception):
    """Episode has no path error"""
