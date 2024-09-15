"""
Kakuyomu CLI

Command line interface for kakuyomu.jp
"""

import click

from kakuyomu.client import Client
from kakuyomu.types.errors import TOMLAlreadyExistsError
from kakuyomu.types.path import Path

from .episode import episode
from .work import work

client = Client(Path.cwd())


@click.group()
def kakuyomu() -> None:
    """
    Kakuyomu CLI

    Command line interface for kakuyomu.jp
    カクヨムの小説投稿・編集をコマンドラインから行うためのツール
    """


# Add subcommands
kakuyomu.add_command(episode)
kakuyomu.add_command(work)


@kakuyomu.command()
def status() -> None:
    """ログインステータスを表示する"""
    print(client.status())


@kakuyomu.command()
def logout() -> None:
    """ログアウトする"""
    client.logout()
    print("logout")


@kakuyomu.command()
@click.option("-email", "-U", type=str, help="Email address", default="")
def login(email: str) -> None:
    """
    ログインする

    ## 環境変数を使用する方法

    以下の環境変数を設定して
    `kakuyomu login` を実行するとログインできます。

    * KAKUYOMU_EMAIL_ADDRESS: カクヨムのユーザー名

    * KAKUYOMU_PASSWORD: カクヨムのパスワード

    ## コマンドからユーザー名とパスワードを入力する方法

    `kakuyomu login -U <email_address>` or
    `kakuyomu login --email <email_address>`

    """
    if email:
        password = click.prompt("Password", hide_input=True)
        client.login(email, password)
    else:
        client.login()
    print(client.status())


@kakuyomu.command()
def init() -> None:
    """現在のディレクトリを小説の1タイトルのrootとして初期化する"""
    try:
        client.initialize_work()
    except TOMLAlreadyExistsError as e:
        print(e)
    except ValueError as e:
        print(f"不正な入力値: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
