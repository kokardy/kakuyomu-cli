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
def login() -> None:
    """ログインする"""
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
