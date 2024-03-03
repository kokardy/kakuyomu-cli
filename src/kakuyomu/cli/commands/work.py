"""Work commands"""

import os

import click

from kakuyomu.client import Client

client = Client(os.getcwd())


@click.group()
def work() -> None:
    """Work commands"""


@work.command("list")
def ls() -> None:
    """List work titles"""
    for work in client.get_works().values():
        print(work)
