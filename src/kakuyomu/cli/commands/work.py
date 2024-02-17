"""Work commands"""
from .kakuyomu import cli, client


@cli.group()
def work() -> None:
    """Work commands"""


@work.command("list")
def ls() -> None:
    """List work titles"""
    for work in client.get_works().values():
        print(work)
