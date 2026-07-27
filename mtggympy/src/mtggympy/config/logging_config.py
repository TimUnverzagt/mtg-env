import logging
from logging.handlers import QueueHandler
from logging import LogRecord
import os
from queue import Queue

UI_LOG_QUEUE: Queue[LogRecord] = Queue()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def create_logger(name: str, logging_level: int, log_to_ui: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    log_path = os.path.join(LOG_DIR, f"{name}.log")
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = logging.FileHandler(log_path, mode="w")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if(log_to_ui):
        ui_handler: QueueHandler = QueueHandler(UI_LOG_QUEUE)
        ui_formatter = logging.Formatter(
        "%(name)s - %(message)s"
    )
        ui_handler.setFormatter(ui_formatter)
        logger.addHandler(ui_handler)

    logger.propagate = False   # Prevent double logging

    return logger


PLAYER_LOG_LEVEL: int = logging.ERROR
# Create the loggers ONCE
main_log   = create_logger("main", logging.ERROR)
ui_log = create_logger("ui", logging.ERROR)
dojo_log = create_logger("dojo", logging.ERROR)
session_log   = create_logger("session", logging.ERROR)
desktop_ui_log   = create_logger("dektop-ui", logging.ERROR)
desktop_api_log   = create_logger("dektop-api", logging.ERROR)
api_log   = create_logger("api", logging.ERROR)
engine_log   = create_logger("engine", logging.ERROR, True)