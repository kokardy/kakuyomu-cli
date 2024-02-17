"""
Kakuyomu CLI

Command line interface for kakuyomu.jp
"""
import os

import click

from kakuyomu.client import Client
from kakuyomu.types.errors import TOMLAlreadyExistsError

client = Client(os.getcwd())


@click.group()
def cli() -> None:
    """
    Kakuyomu CLI

    Command line interface for kakuyomu.jp
    """


@cli.command()
def status() -> None:
    """Show login status"""
    print(client.status())


@cli.command()
def logout() -> None:
    """Logout"""
    client.logout()
    print("logout")


@cli.command()
def login() -> None:
    """Login"""
    client.login()
    print(client.status())


@cli.command()
def init() -> None:
    """Initialize work toml"""
    try:
        client.initialize_work()
    except TOMLAlreadyExistsError as e:
        print(e)
    except ValueError as e:
        print(f"不正な入力値: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
