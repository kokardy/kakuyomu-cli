"""Episode commands"""
import os

import click

from .kakuyomu import cli, client


@cli.group()
def episode() -> None:
    """Episode commands"""
    pass


@episode.command("list")
def ls() -> None:
    """List episode titles"""
    for i, episode in enumerate(client.get_episodes()):
        print(i, episode)


@episode.command()
@click.argument("filepath")
def link(filepath: str) -> None:
    """Link episodes"""
    filepath = os.path.join(os.getcwd(), filepath)
    config_dir = client.config_dir
    relative_path = os.path.relpath(filepath, config_dir)
    try:
        episode = client.link_file(relative_path)
        print("linked", episode)
    except Exception as e:
        print(f"リンクに失敗しました: {e}")

@episode.command()
def unlink() -> None:
    """Unlink episodes"""
    try:
        client.unlink()
    except Exception as e:
        print(f"リンクに失敗しました: {e}")
        raise e


@episode.command()
def create() -> None:
    """Create episode"""
    # client.create_episode()
    print("not implemented yet")


@episode.command()
def publish() -> None:
    """Publish episode"""
    # client.publish_episode()
    print("not implemented yet")
