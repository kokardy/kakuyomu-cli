"""Login variables"""

import os
from typing import Final

from pydantic import BaseModel
from pydantic.types import SecretStr

EMAIL_ADDRESS_KEY: Final[str] = "KAKUYOMU_EMAIL_ADDRESS"
PASSWORD_KEY: Final[str] = "KAKUYOMU_PASSWORD"


class Login(BaseModel):
    """Login"""

    EMAIL_ADDRESS: str = os.environ.get(EMAIL_ADDRESS_KEY, "")
    PASSWORD: SecretStr = SecretStr(os.environ.get(PASSWORD_KEY, ""))

    @classmethod
    def set(cls, email: str, password: str) -> None:
        """Set login"""
        cls.EMAIL_ADDRESS = email
        cls.PASSWORD = SecretStr(password)

    def __str__(self) -> str:
        """Return string representation of login"""
        return f"EMAIL_ADDRESS: {self.EMAIL_ADDRESS}, PASSWORD: {self.PASSWORD}"
