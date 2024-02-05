"""テスト用のクラスを定義するモジュール"""
import os
from typing import Callable, ClassVar

from kakuyomu.client import Client
from kakuyomu.types import Work

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

    client: Client = None

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        super().setup_class()

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """作業ディレクトリにwork.tomlファイルが存在しない状態でClientを生成する"""
        super().setup_method(method)
        if not self.client:
            self.client = createClient(case=Case.NO_WORK_TOML)
        # TOMLファイルが存在する場合は削除しておく
        if os.path.exists(self.client.work_toml_path):
            os.remove(self.client.work_toml_path)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """残っているtomlファイルを削除する"""
        super().teardown_method(method)
        # TOMLファイルが存在する場合は削除しておく
        if os.path.exists(self.client.work_toml_path):
            os.remove(self.client.work_toml_path)


class NoEpisodesTest(Test):
    """エピソードが存在しない場合のテスト"""

    client: Client = None

    WORK: ClassVar[Work] = Work(
        id="16816927859498193192",
        title="アップロードテスト用",
        episodes=[],
    )

    # initialize class
    @classmethod
    def setup_class(cls) -> None:
        """テストクラスの初期化処理"""
        super().setup_class()

    # run before all test functions
    def setup_method(self, method: Callable[..., None]) -> None:
        """作業ディレクトリにwork.tomlファイルが存在する状態でClientを生成する"""
        super().setup_method(method)
        if not self.client:
            self.client = createClient(case=Case.NO_EPISODES)
        # episodesが空のworkに置き換えておく
        self.client._dump_work_toml(self.__class__.WORK)

    # run after all test functions
    def teardown_method(self, method: Callable[..., None]) -> None:
        """残っているtomlファイルを削除する"""
        super().teardown_method(method)
        # episodesが空のworkに置き換えておく
        self.client._dump_work_toml(self.__class__.WORK)
