class Test:
    # テスト毎にテスト名を表示する
    def setup_method(self, method) -> None:
        print(f"\n========== method: {method.__name__} ============")
