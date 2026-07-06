from enum import Enum

#Misc
GAMEOVER : str = "Game over!"

#Decision details
CARD_TO_PLAY: str = "Card to play"

#Zones

#Actions
#DRAW_A_CARD: str = "Draw a Card"

#Replacement Effects
DECKING: str = "Decking"

class CardType(Enum):
    UNKNOWN = 0
    LAND = 1
    CREATURE = 2

class ManaColor(Enum):
    COLORLESS = 0
    WHITE = 1
    BLUE = 2
    BLACK = 3
    RED = 4
    GREEN = 5

class Zone(Enum):
    LIBRARY = 0
    HAND = 1
    BATTLEFIELD = 2

class Phase(Enum):
    BEGINNING = 0
    MAINPHASE_1 = 1
    COMBAT = 2
    MAINPHASE_2 = 3
    END = 4

class GameStep(Enum):
    UPKEEP = (Phase.BEGINNING, 0)
    DRAW = (Phase.BEGINNING, 1)
    MAIN_1 = (Phase.MAINPHASE_1, 0)
    ATTACK_STEP = (Phase.COMBAT, 0)
    BLOCK_STEP = (Phase.COMBAT, 1)
    MAIN_2 = (Phase.MAINPHASE_2, 0)
    END_STEP = (Phase.END, 0)

class DeathDescription(Enum):
    LIFETOTAL = "having 0 or less life"
    DECKING = "drawing from an empty library"
    
