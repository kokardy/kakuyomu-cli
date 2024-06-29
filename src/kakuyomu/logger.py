"""Module for logging"""

import logging

import coloredlogs

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
coloredlogs.install(logger=logger)


def get_logger() -> logging.Logger:
    """Get logger"""
    return logger
