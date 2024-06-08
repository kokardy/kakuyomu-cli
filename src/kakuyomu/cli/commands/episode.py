"""Episode commands"""
import datetime

import click

from kakuyomu.client import Client
from kakuyomu.types.errors import EpisodeReservePublishError
from kakuyomu.types.path import Path

client = Client(Path.cwd())


@click.group()
def episode() -> None:
    """Episode commands"""
    pass


@episode.command("list")
def ls() -> None:
    """List episode titles"""
    for i, episode in enumerate(client.get_remote_episodes()):
        print(i, episode)


@episode.command
def fetch() -> None:
    """Fetch remote episodes to work.toml"""
    diff = client.fetch_remote_episodes()
    print(diff)


@episode.command()
@click.argument("filepath")
def link(file: str) -> None:
    """Link episodes"""
    cwd = Path.cwd()
    path = Path(file)
    filepath = Path.joinpath(cwd, path)
    config_dir = client.config_dir
    relative_path = config_dir.relative_to(filepath)
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
@click.argument("filepath")
def create(title: str, file: str) -> None:
    """Create episode"""
    filepath = Path(file)
    client.create_remote_episode(title=title, filepath=filepath)
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
    episode = client.update_remote_episode()
    print(f"エピソードを更新しました: {episode}")


@episode.command()
@click.argument("publish_at_str")
def publish(publish_at_str: str) -> None:
    """Publish episode"""
    if publish_at_str == "cancel":
        client.cancel_reservation()
        return
    date_format = "%Y/%m/%d %H:%M"
    try:
        publish_at = datetime.datetime.strptime(publish_at_str, date_format)
        client.reserve_publishing_episode(publish_at)
    except EpisodeReservePublishError as e:
        print(f"予約公開/キャンセルに失敗しました: {e}")
    except ValueError as e:
        print(f"日時は{date_format}の形式で入力してください: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
