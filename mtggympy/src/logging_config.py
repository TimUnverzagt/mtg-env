import logging
import os

LOG_DIR = "./../../logs"
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
main_log   = create_logger("main", logging.INFO)
ui_log = create_logger("ui", logging.INFO)
dojo_log = create_logger("dojo", logging.INFO)
session_log   = create_logger("session", logging.INFO)
api_log   = create_logger("api", logging.INFO)
engine_log   = create_logger("engine", logging.INFO)