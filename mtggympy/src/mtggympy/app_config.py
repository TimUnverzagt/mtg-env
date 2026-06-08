import logging
import os

# file --> config --> module --> src
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HUMAN_RENDERING: bool = False

SESSION_TICK_LENGTH: float = 0#.2
AGENT_TICK_LENGTH: float = 0#.137
API_TICK_LENGTH: float = 0#.1
STARTING_LIFE: int = 20
DECK_SIZE: int = 40


PLAYER_LOG_LEVEL: int = logging.WARN