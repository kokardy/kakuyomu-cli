import coloredlogs

from kakuyomu.logger import get_logger


def set_color() -> None:
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "critical": {"color": "red", "bold": True},
        "error": {"color": "red"},
        "warning": {"color": "yellow"},
        "notice": {"color": "magenta"},
        "info": {},
        "debug": {"color": "green"},
        "spam": {"color": "green", "faint": True},
        "success": {"color": "green", "bold": True},
        "verbose": {"color": "blue"},
    }
    logger = get_logger()
    coloredlogs.install(level="INFO", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")
    coloredlogs.install(level="DEBUG", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")
    coloredlogs.install(level="WARN", logger=logger, fmt="%(asctime)s : %(message)s", datefmt="%Y/%m/%d %H:%M:%S")


set_color()
