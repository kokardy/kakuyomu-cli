"""setting utils"""
import os


class Env:
    """Environment variables"""

    @classmethod
    def get(cls, key: str) -> str:
        """Get environment variable"""
        return os.environ.get(key, "")
