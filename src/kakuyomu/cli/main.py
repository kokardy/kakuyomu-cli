"""Main entry point for the CLI"""

from .commands import kakuyomu


def main() -> None:
    """CLI entry point"""
    kakuyomu()


if __name__ == "__main__":
    main()
