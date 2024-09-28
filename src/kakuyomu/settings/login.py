"""Login variables"""

from typing import Annotated, Final, Self

from pydantic import BaseModel, Field, model_validator
from pydantic.types import SecretStr

from .utils import Env

EMAIL_ADDRESS_KEY: Final[str] = "KAKUYOMU_EMAIL_ADDRESS"
PASSWORD_KEY: Final[str] = "KAKUYOMU_PASSWORD"


class Login(BaseModel):
    """Login"""

    # type check のために代入式を使用しているが
    # default_factoryが優先されて、右辺の値は無視される
    email: Annotated[str, Field(default_factory=lambda: Env.get(EMAIL_ADDRESS_KEY))] = ""
    password: Annotated[SecretStr, Field(default_factory=lambda: SecretStr(Env.get(PASSWORD_KEY)))] = SecretStr("")

    def __setattr__(self, name: str, value: str | SecretStr) -> None:
        """Set attribute"""
        if name == "password":
            if isinstance(value, str):
                super().__setattr__(name, SecretStr(value))
                return
        super().__setattr__(name, value)

    def __str__(self) -> str:
        """Return string representation of login"""
        return f"EMAIL_ADDRESS: {self.email}, PASSWORD: {self.password}"

    @model_validator(mode="after")
    def not_null_validation(self) -> Self:
        """Validate email and password"""
        if not self.email:
            raise ValueError("Email address is required")
        if not self.password:
            raise ValueError("Password is required")

        return self
