"""Decorators for the client"""

from functools import wraps
from typing import Callable, Concatenate, Self

from kakuyomu.types.errors import NotLoginError


def require_login[**P, R](func: Callable[Concatenate[Self, P], R]) -> Callable[Concatenate[Self, P], R]:  # type: ignore[valid-type, name-defined]
    """Require login"""

    @wraps(func)
    def inner(self: Self, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        """Return result wrapped function"""
        if not self.status().is_login:
            raise NotLoginError("Not Login")
        return func(self, *args, **kwargs)

    return inner
