"""Kakuyomu CLI

Command line interface for kakuyomu.jp
"""
import click

from kakuyomu.client import Client

client = Client()


@click.group()
def cli() -> None:
    """Kakuyomu CLI

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


def main() -> None:
    """CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
