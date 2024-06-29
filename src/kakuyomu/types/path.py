"""Path module"""

from functools import cached_property
from pathlib import Path as _Path

from kakuyomu.logger import logger
from kakuyomu.settings import CONFIG_DIRNAME


class Path(_Path):
    """Path class with additional methods"""

    @cached_property
    def config_dir(self) -> "ConfigDir":
        """Get the work root directory"""
        root = self.root
        cwd = self
        while True:
            path = Path.joinpath(cwd, Path(CONFIG_DIRNAME))
            if path.exists():
                if path.is_dir():
                    logger.info(f"work dir found: {cwd}")
                    config_path = cwd.joinpath(CONFIG_DIRNAME)
                    config_dir = ConfigDir(config_path)
                    return config_dir
            cwd = self.parent
            if cwd.name == root:
                raise FileNotFoundError(f"{CONFIG_DIRNAME} not found")

    @cached_property
    def work_root(self) -> "Path":
        """Get the work root directory"""
        config_dir = self.config_dir
        return config_dir.parent


class ConfigDir(Path):
    """Work project ConfigDir"""

    @cached_property
    def work_toml(self) -> Path:
        """Get the work toml file"""
        return Path.joinpath(self, "work.toml")

    @cached_property
    def cookie(self) -> Path:
        """Get the cookie file"""
        return Path.joinpath(self, "cookie")
