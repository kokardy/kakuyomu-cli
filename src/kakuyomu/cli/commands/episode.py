"""Episode commands"""

import datetime

import click

from kakuyomu.client import Client
from kakuyomu.types.errors import EpisodeReservePublishError
from kakuyomu.types.path import Path

client = Client(Path.cwd())


@click.group()
def episode() -> None:
    """エピソード関係のコマンド"""
    pass


@episode.command("list")
def ls() -> None:
    """エピソードをリスト表示する"""
    for i, episode in enumerate(client.get_remote_episodes()):
        print(i, episode)


@episode.command
def fetch() -> None:
    """リモートのエピソードをwork.tomlに同期する"""
    diff = client.fetch_remote_episodes()
    print(diff)


@episode.command()
@click.argument("filepath")
@click.option("--filter", "-F", type=str, default="")
def link(file: str, filter: str) -> None:
    """work.tomlのエピソードにファイルパスを設定する"""
    cwd = Path.cwd()
    path = Path(file)
    filepath = Path.joinpath(cwd, path)
    config_dir = client.config_dir
    relative_path = config_dir.relative_to(filepath)
    try:
        episode = client.link_file(relative_path, filter_text=filter)
        print("linked", episode)
    except Exception as e:
        print(f"リンクに失敗しました: {e}")


@episode.command()
@click.option("--filter", "-F", type=str, default="")
def unlink(filter: str) -> None:
    """エピソードからファイルパス設定を削除する"""
    try:
        client.unlink(filter_text=filter)
    except Exception as e:
        print(f"リンクに失敗しました: {e}")
        raise e


@episode.command()
@click.argument("title")
@click.argument("file")
def create(title: str, file: str) -> None:
    """
    リモートにエピソードを作成する

    Args:
    ----
        title: エピソードのタイトル
        file: エピソードのファイルパス

    """
    filepath = Path(file).absolute()
    client.create_remote_episode(title=title, filepath=filepath)
    print(f"エピソードを作成しました: {title}")


@episode.command()
@click.option("--line", "-l", type=int, default=3)
@click.option("--filter", "-F", type=str, default="")
def show(line: int, filter: str) -> None:
    """
    エピソードの内容を表示する

    Args:
    ----
        line: 表示する行数
        filter: エピソードフィルタ文字列. これをIDかタイトルに含むエピソードを表示する

    """
    body = client.get_remote_episode_body(filter_text=filter)
    count = 0
    for row in body:
        if count >= line:
            break
        try:
            # 空白行はスキップ
            if row.strip() == "":
                continue
            print(row)  # 行表示
            count += 1
        except StopIteration:
            return
        except Exception as e:
            print(f"予期しないエラー: {e}")


@episode.command()
@click.option("--filter", "-F", type=str, default="")
def update(filter: str = "") -> None:
    """リモートエピソードの内容をリンクされているファイルの内容に更新する"""
    episode = client.update_remote_episode(filter_text=filter)
    print(f"エピソードを更新しました: {episode}")


@episode.command()
@click.argument("publish_at_str")
@click.option("--filter", "-F", type=str, default="")
def publish(publish_at_str: str, filter: str) -> None:
    """エピソードの公開予約を行う"""
    if publish_at_str == "cancel":
        client.cancel_reservation(filter_text=filter)
        return
    date_format = "%Y/%m/%d %H:%M"
    try:
        publish_at = datetime.datetime.strptime(publish_at_str, date_format)
        client.reserve_publishing_episode(publish_at, filter_text=filter)
    except EpisodeReservePublishError as e:
        print(f"予約公開/キャンセルに失敗しました: {e}")
    except ValueError as e:
        print(f"日時は{date_format}の形式で入力してください: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
