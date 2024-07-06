# kakuyomu CLI

Command line interface for kakuyomu.jp writers.

## install

`pip install kakuyomu-cli`

`kakuyomu --help`

# Commands

## Kakuyomu command

`kakuyomu --help`

```
Usage: kakuyomu [OPTIONS] COMMAND [ARGS]...

  Kakuyomu CLI

  Command line interface for kakuyomu.jp カクヨムの小説投稿・編集をコマンドラインから行うためのツール

Options:
  --help  Show this message and exit.

Commands:
  episode  エピソード関係のコマンド
  init     現在のディレクトリを小説の1タイトルのrootとして初期化する
  login    ログインする
  logout   ログアウトする
  status   ログインステータスを表示する
  work     小説タイトルに関するコマンド
```

## Work commands

`kakuyomu work --help`

```
Usage: kakuyomu work [OPTIONS] COMMAND [ARGS]...

  小説タイトルに関するコマンド

Options:
  --help  Show this message and exit.

Commands:
  list  小説タイトルの一覧を表示する
```

## Episode commands

`kakuyomu episode --help`

```
Usage: kakuyomu episode [OPTIONS] COMMAND [ARGS]...

  エピソード関係のコマンド

Options:
  --help  Show this message and exit.

Commands:
  create   リモートにエピソードを作成する
  fetch    リモートのエピソードをwork.tomlに同期する
  link     work.tomlのエピソードにファイルパスを設定する
  list     エピソードをリスト表示する
  publish  エピソードの公開予約を行う
  show     エピソードの内容を表示する
  unlink   エピソードからファイルパス設定を削除する
  update   リモートエピソードの内容をリンクされているファイルの内容に更新する
```

## usage

1.  小説のルートディレクトリに移動
2.  ログイン `kakuyomu login`
3.  初期設定 `kakuyomu init` 小説を選択
