"""Work commands"""

import click

from kakuyomu.client import Client
from kakuyomu.types.path import Path

client = Client(Path.cwd())


@click.group()
def work() -> None:
    """Work commands"""


@work.command("list")
def ls() -> None:
    """List work titles"""
    for work in client.get_works().values():
        print(work)
