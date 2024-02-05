"""Decorators for the client"""
from typing import Callable, Concatenate, Self

from kakuyomu.types.errors import NotLoginError, WorkNotSetError


def require_login[**P, R](func: Callable[Concatenate[Self, P], R]) -> Callable[P, R]:  # type: ignore
    """Require login"""

    def inner(self, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        """Return result wrapped function"""
        if not self.status().is_login:
            raise NotLoginError("Not Login")
        return func(self, *args, **kwargs)

    return inner


def require_work[**P, R](func: Callable[Concatenate[Self, P], R]) -> Callable[P, R]:  # type: ignore
    """Require work toml is set"""

    def inner(self, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        """Return result wrapped function"""
        if not self.work:
            raise WorkNotSetError("work toml is not set")
        return func(self, *args, **kwargs)

    return inner
