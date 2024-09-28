"""Test Login model"""


from typing import Annotated

import pytest
from pydantic import BaseModel, Field, ValidationError
from pydantic.types import SecretStr
from pytest_mock import MockFixture

from src.kakuyomu.settings import Login
from src.kakuyomu.settings.login import EMAIL_ADDRESS_KEY, PASSWORD_KEY
from src.kakuyomu.settings.utils import Env


class TestLogin:
    """Test Login"""

    def test_default_value(self) -> None:
        """
        Pydanticのデフォルト値の挙動を確認する

        代入式ではなくdefault_factoryが優先されることを確認する

        """

        class _A(BaseModel):
            a: Annotated[str, Field(default_factory=lambda: "a")] = "b"

        a = _A()
        assert a.a == "a"

    def test_secret(self) -> None:
        """Test login"""
        email = "test@email.com"
        password = "test_password"
        login = Login(email=email, password=SecretStr(password))
        assert login.email
        assert login.password
        assert login.password != password

    def test_null_value(self, mocker: MockFixture) -> None:
        """Test null value"""
        mock_environ = {
            EMAIL_ADDRESS_KEY: "",
            PASSWORD_KEY: "",
        }
        mocker.patch.dict("os.environ", mock_environ)
        mocker.patch.object(Env, "get", return_value="")

        assert Env.get(EMAIL_ADDRESS_KEY) == ""
        assert Env.get(PASSWORD_KEY) == ""
        with pytest.raises(ValidationError) as e:
            account = Login()
            print(f"{ account= }")
        print(f"{ e.value= }")
        assert " is required" in str(e.value)
