import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def create_logger(name: str, logging_level: int) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    log_path = os.path.join(LOG_DIR, f"{name}.log")
    handler = logging.FileHandler(log_path, mode="w")
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False   # Prevent double logging

    return logger


# Create the loggers ONCE
main_log   = create_logger("main", logging.ERROR)
ui_log = create_logger("ui", logging.ERROR)
dojo_log = create_logger("dojo", logging.ERROR)
session_log   = create_logger("session", logging.ERROR)
api_log   = create_logger("api", logging.ERROR)
engine_log   = create_logger("engine", logging.ERROR)