"""テスト用のヘルパー関数を定義するモジュール"""
from typing import Callable


class Test:
    """テスト毎にテスト名を表示する"""

    def setup_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの前にテスト名を表示する"""
        print(f"\n========== method: {method.__name__} ============")
