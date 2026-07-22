from enum import Enum
import os

from mtggympy.config.decks import DeckName

###############
# Setup 
###############
class Setup(Enum):
    TRAINING = 0
    HUMAN_VS_INTERNALS = 1
    GOLDFISH_SPEED_EXP = 2
    MONKEY_SPEED_EXP = 3
    RULESBASED_SPEED_EXP = 4

CURRENT_SETUP: Setup = Setup.TRAINING
DEFAULT_DECK: DeckName = DeckName.COLORLESS_40

EPISODES_IN_EXPERIMENT: int = 100

TRASITION_WITH_STATE_BACKUP: bool = True

###############
# Project 
###############
# file --> config --> module --> src
SRC_DIR = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."), "..")
ASSET_DIR = os.path.join(SRC_DIR, "assets")
EXPERIMENT_RESULT_DIR = os.path.join(SRC_DIR, "experiments")

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
