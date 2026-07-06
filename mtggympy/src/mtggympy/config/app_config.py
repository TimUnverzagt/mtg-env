from enum import Enum
import logging
import os

###############
# Setup 
###############
class Setup(Enum):
    Q_TRAINING = 0
    HUMAN_VS_INTERNALS = 1
    GOLDFISH_SPEED_EXP = 2
    MONKEY_SPEED_EXP = 3
    RULESBASED_SPEED_EXP = 4

CURRENT_SETUP: Setup = Setup.MONKEY_SPEED_EXP

EPISODES_IN_EXPERIMENT: int = 1000

###############
# Project 
###############
# file --> config --> module --> src
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(os.path.join(SRC_DIR, ".."), "assets")
PLAYER_LOG_LEVEL: int = logging.ERROR

###############
# UI 
###############
HUMAN_RENDERING: bool = False
UI_STARTING_WIDTH = 1920
UI_STARTING_HEIGHT = 1080
CARD_HEIGHT = 187
CARD_WH_RATIO = 63/88

###############
# Logic
###############
SESSION_TICK_LENGTH: float = 0#.2
AGENT_TICK_LENGTH: float = 0#.137
API_TICK_LENGTH: float = 0#.1
STARTING_LIFE: int = 20
DECK_SIZE: int = 40

