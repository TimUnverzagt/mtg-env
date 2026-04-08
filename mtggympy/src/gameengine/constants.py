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
    MAINPHASE = 0
    COMBAT = 1

# TODO: Make into proper class/type
class Action(Enum):
    PASS = 0
    PLAY_CARD = 1
    ATTACK = 2
    ACTIVATE_LANDS = 3