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
@click.argument("title")
@click.argument("file_path")
def create(title: str, file_path: str) -> None:
    """Create episode"""
    client.create_remote_episode(title=title, file_path=file_path)
    print(f"エピソードを作成しました: {title}")


@episode.command()
@click.option("--line", "-l", type=int, default=3)
def show(line: int) -> None:
    """
    Show episode contents

    Args:
    ----
        line (int): 表示する行数

    """
    body = client.get_remote_episode_body()
    count = 0
    for row in body:
        if count >= line:
            break
        try:
            # 空白行はスキップ
            if row.strip() == "":
                continue
            print(row)
            count += 1
        except StopIteration:
            return
        except Exception as e:
            print(f"予期しないエラー: {e}")


@episode.command()
def update() -> None:
    """Update episode"""
    print("not implemented yet")


@episode.command()
def publish() -> None:
    """Publish episode"""
    # client.publish_episode()
    print("not implemented yet")
