import logging
from logging.handlers import QueueHandler
from logging import LogRecord
import os
from queue import Queue

UI_LOG_QUEUE: Queue[LogRecord] = Queue()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def create_logger(name: str, logging_level: int, log_to_ui: bool = False, dry_run: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    if dry_run:
        return logger
    log_path = os.path.join(LOG_DIR, f"{name}.log")
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
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


PLAYER_LOG_LEVEL: int = logging.DEBUG
PLAYER_LOG_DRY_RUN: bool = False
# Create the loggers ONCE
player_0_log = create_logger("player_0", logging.DEBUG)
player_1_log = create_logger("player_1", logging.DEBUG)
main_log   = create_logger("main", logging.ERROR)
ui_log = create_logger("ui", logging.ERROR)
dojo_log = create_logger("dojo", logging.ERROR)
session_log   = create_logger("session", logging.INFO)
desktop_ui_log   = create_logger("dektop-ui", logging.ERROR)
desktop_api_log   = create_logger("dektop-api", logging.ERROR)
api_log   = create_logger("api", logging.DEBUG)
engine_log   = create_logger("engine", logging.INFO, True)