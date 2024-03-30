# kakuyomu CLI

Command line interface for kakuyomu.jp writers.

## install

`pip install kakuyomu-cli`

`kakuyomu --help`

# Commands

| command | description          |
| -----   | ----                 |
| init    | Initialize work toml |
| login   | Login                |
| logout  | Logout               |
| status  | Show login status    |
| work    | Work commands        |
| episode | Episode commands     |


## Work Commands

ex)
`kakuyomu work list`

```
Options:
  --help  Show this message and exit.

Commands:
  list  List work titles
```

## Episode Commands

ex)
`kakuyomu episode list`

```
Options:
  --help  Show this message and exit.

Commands:
  create   Create episode
  link     Link episodes
  list     List episode titles
  publish  Publish episode
  show     Show episode contents
  unlink   Unlink episodes
  update   Update episode
```

## usage

1.  小説のルートディレクトリに移動
2.  ログイン `kakuyomu login`
3.  初期設定 `kakuyomu init` 小説を選択
