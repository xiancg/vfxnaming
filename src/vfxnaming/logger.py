import logging
import sys
import json
from datetime import date
from pathlib import Path
from typing import AnyStr, Tuple


class Logger:
    LEVEL_DEFAULT = logging.INFO

    def __init__(self, logger_name, propagate=False):
        self.name = logger_name
        self.__logger_obj = None
        self.propagate = propagate
        self.file_handler = None

    @property
    def logger_obj(self) -> logging.Logger:
        if not self.__logger_obj:
            if self.logger_exists(self.name):
                self.__logger_obj = logging.getLogger(self.name)
            else:
                self.__logger_obj = logging.getLogger(self.name)
                self.__logger_obj.setLevel(self.LEVEL_DEFAULT)
                self.__logger_obj.propagate = self.propagate

                formatter = logging.Formatter(
                    "[%(asctime)s:%(module)s:%(funcName)s:"
                    "%(lineno)s:%(levelname)s] %(message)s"
                )

                stream_handler = logging.StreamHandler(sys.stderr)
                stream_handler.setFormatter(formatter)
                self.__logger_obj.addHandler(stream_handler)

        return self.__logger_obj

    @staticmethod
    def logger_exists(name: AnyStr) -> bool:
        return name in logging.Logger.manager.loggerDict.keys()

    def set_level(self, level):
        self.logger_obj.setLevel(level)

    def debug(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.debug(msg, *args, **kwargs)

    def info(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.info(msg, *args, **kwargs)

    def warning(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.warning(msg, *args, **kwargs)

    def error(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.error(msg, *args, **kwargs)

    def critical(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.critical(msg, *args, **kwargs)

    def log(self, level, msg: AnyStr, *args, **kwargs):
        self.logger_obj.log(level, msg, *args, **kwargs)

    def exception(self, msg: AnyStr, *args, **kwargs):
        self.logger_obj.exception(msg, *args, **kwargs)

    def log_to_file(self, level=logging.DEBUG):
        log_file_path: Path = self.get_log_file_path()

        try:
            if not log_file_path.parent.exists():
                log_file_path.parent.mkdir()
        except (OSError, IOError) as why:
            raise why

        self.file_handler = logging.FileHandler(log_file_path, mode="a")
        self.file_handler.setLevel(level)

        formatter = logging.Formatter(
            "[%(asctime)s:%(module)s:%(funcName)s:"
            "%(lineno)s:%(levelname)s] %(message)s"
        )

        self.file_handler.setFormatter(formatter)
        self.logger_obj.addHandler(self.file_handler)

    def stop_logging_to_file(self):
        if self.file_handler:
            self.logger_obj.removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None

    def get_log_file_path(self) -> Path:
        user_path = Path("~").expanduser()
        module_dir = Path(__file__).parents[0]
        config_location = module_dir / "cfg/config.json"
        config = {}
        with open(config_location) as fp:
            config = json.load(fp)
        final_dir = user_path / f".{config.get('cfg_dir_name')}"
        today = date.today()
        date_string = today.strftime("%d-%m-%Y")
        log_file_path = final_dir / f"{self.logger_obj.name}_{date_string}.log"

        return log_file_path


def init_logger(
    base_name: AnyStr, log_to_file: bool = False
) -> Tuple[logging.Logger, logging.Logger]:
    """
    Initialize 'base_name' logging object and add a STDOUT handler to output to
    console, terminal, etc.

    Args:
        base_name (str): Base name for the logger. Will be used to create the logger name.
        log_to_file (bool): If True, the logger will log to a file.

    Returns:
        tuple: Tuple containing: logger, logger_gui (child of logger and used for GUI messages)
    """
    logger = Logger(f"{base_name}log")
    if log_to_file:
        logger.log_to_file()

    logger_gui = Logger(f"{base_name}log.gui", propagate=True)
    logger_gui.set_level(logging.INFO)

    return logger, logger_gui


logger, logger_gui = init_logger("vfxnaming")


if __name__ == "__main__":
    pass
