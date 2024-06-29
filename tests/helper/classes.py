"""テスト用のクラスを定義するモジュール"""

from typing import Callable, ClassVar

from kakuyomu.client import Client
from kakuyomu.types import Work
from kakuyomu.types.path import Path

from .functions import Case, createClient, logger


class Test:
    """
    共通テストクラス

    * テスト毎にテスト名を表示する
    """

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        pass

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの前にテスト名を表示する"""
        logger.debug(f"\n========== START {self.__class__} method: {method.__name__} ============")

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの後にテスト名を表示する"""
        logger.debug(f"\n========== END {self.__class__} method: {method.__name__} ============")


class WorkTOMLNotExistsTest(Test):
    """tomlファイルが存在しない場合のテスト"""

    client: Client

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        super().setup_class()
        cls.client = createClient(case=Case.NO_WORK_TOML)
        # TOMLファイルが存在する場合は削除しておく
        cls.client.config_dir.work_toml.unlink(missing_ok=True)

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """作業ディレクトリにwork.tomlファイルが存在しない状態でClientを生成する"""
        super().setup_method(method)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """残っているtomlファイルを削除する"""
        super().teardown_method(method)
        # TOMLファイルが存在する場合は削除しておく
        self.client.config_dir.work_toml.unlink(missing_ok=True)


class NoEpisodeTest(Test):
    """エピソードが存在しない場合のテスト"""

    client: Client

    WORK: ClassVar[Work] = Work(id="16816927859498193192", title="アップロードテスト用", episodes={})

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        super().setup_class()
        cls.client = createClient(case=Case.NO_EPISODES)
        # episodesが空のworkに置き換えておく
        cls.client._dump_work_toml(cls.WORK)

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """作業ディレクトリにwork.tomlファイルが存在する状態でClientを生成する"""
        super().setup_method(method)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """残っているtomlファイルを削除する"""
        super().teardown_method(method)
        # episodesが空のworkに置き換えておく
        self.client._dump_work_toml(self.__class__.WORK)


class EpisodeExistsTest(Test):
    """エピソードが存在する場合のテスト"""

    client: Client
    TOML: ClassVar[Path] = Path(__file__).parent.joinpath("work.toml")
    WORK: ClassVar[Work] = Work.load(TOML)

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        super().setup_class()
        cls.client = createClient(case=Case.EPISODES_EXISTS)
        # episodesがある状態のworkに置き換えておく
        cls.client._dump_work_toml(cls.WORK)

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """作業ディレクトリにwork.tomlファイルが存在する状態でClientを生成する"""
        super().setup_method(method)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """残っているtomlファイルを削除する"""
        super().teardown_method(method)
        # episodesがある状態のworkに置き換えておく
        self.client._dump_work_toml(self.__class__.WORK)
