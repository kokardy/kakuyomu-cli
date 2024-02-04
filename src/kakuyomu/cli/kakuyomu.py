"""
Kakuyomu CLI

Command line interface for kakuyomu.jp
"""
import click
import os

from kakuyomu.client import Client
from kakuyomu.types.errors import TOMLAlreadyExists

client = Client(os.getcwd())


@click.group()
def cli() -> None:
    """
    Kakuyomu CLI

    Command line interface for kakuyomu.jp
    """
    pass


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


@cli.command()
def episodes() -> None:
    """List episodes titles"""
    for episode in client.get_episodes().values():
        print(episode)

@cli.command()
def init() -> None:
    """Initialize work toml"""
    try:
        client.initialize_work()
    except TOMLAlreadyExists as e:
        print(e)
    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"unexpected error: {e}")

def main() -> None:
    """CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
