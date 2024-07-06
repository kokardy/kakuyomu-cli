"""Work commands"""

import click

from kakuyomu.client import Client
from kakuyomu.types.path import Path

client = Client(Path.cwd())


@click.group()
def work() -> None:
    """小説タイトルに関するコマンド"""


@work.command("list")
def ls() -> None:
    """小説タイトルの一覧を表示する"""
    for i, work in enumerate(client.get_works().values()):
        print(f"{i}: {work}")
