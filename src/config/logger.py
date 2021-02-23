from logging import DEBUG, FileHandler, Formatter, Logger, StreamHandler, getLogger
from pathlib import Path


def _get_app_logger() -> Logger:
    logger = getLogger("app")
    logger.setLevel(DEBUG)
    return logger


def _get_console_handler() -> StreamHandler:
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter("[%(levelname)s] %(message)s"))
    return handler


def _get_file_handler() -> FileHandler:
    filename = Path(__file__).parent.parent / "app.log"
    handler = FileHandler(filename)
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter("[%(levelname)s] %(message)s"))
    return handler


app_logger = _get_app_logger()
console_handler = _get_console_handler()
file_handler = _get_file_handler()
