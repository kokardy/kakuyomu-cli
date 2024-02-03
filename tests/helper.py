"""テスト用のヘルパー関数を定義するモジュール"""
import logging
from typing import Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)


class Test:
    """テスト毎にテスト名を表示する"""

    def setup_method(self, method: Callable[..., None]) -> None:
        """テストメソッドの前にテスト名を表示する"""
        logger.debug(f"\n========== method: {method.__name__} ============")
