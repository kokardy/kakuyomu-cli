"""
Kakuyomu CLI

Command line interface for kakuyomu.jp
"""
import os

import click

from kakuyomu.client import Client
from kakuyomu.types.errors import TOMLAlreadyExists

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
def works() -> None:
    """List work titles"""
    for work in client.get_works().values():
        print(work)


@cli.group()
def episode() -> None:
    """Episode commands"""
    pass


@episode.command()
def ls() -> None:
    """List episode titles"""
    for i, episode in enumerate(client.get_episodes().values()):
        print(i, episode)


@episode.command()
def link() -> None:
    """Link episodes"""
    # client.link_episodes()
    print("linked")


@cli.command()
def init() -> None:
    """Initialize work toml"""
    try:
        client.initialize_work()
    except TOMLAlreadyExists as e:
        print(e)
    except ValueError as e:
        print(f"不正な入力値: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")


def main() -> None:
    """CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
