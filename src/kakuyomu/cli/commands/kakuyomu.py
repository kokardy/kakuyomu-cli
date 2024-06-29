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
    """


# Add subcommands
kakuyomu.add_command(episode)
kakuyomu.add_command(work)


@kakuyomu.command()
def status() -> None:
    """Show login status"""
    print(client.status())


@kakuyomu.command()
def logout() -> None:
    """Logout"""
    client.logout()
    print("logout")


@kakuyomu.command()
def login() -> None:
    """Login"""
    client.login()
    print(client.status())


@kakuyomu.command()
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
