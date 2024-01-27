"""settings"""

from .const import CONFIG_DIRNAME, URL, WORK_FILENAME, Login
from .work import COOKIE, get_work

__all__ = ["URL", "Login", "CONFIG_DIRNAME", "WORK_FILENAME",  "get_work", "COOKIE"]
