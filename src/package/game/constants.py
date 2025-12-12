from game.decision_event import DecisionEvent
from game.card_info import CardInfo

#Misc
GAMEOVER : str = "Game over!"

#Phases
MAINPHASE: str = "Mainphase"
COMBAT: str = "Combat"

#Decisions
MAINPHASE_PASS: str = "Pass"
MAINPHASE_PLAY_CREATURE: str = "Play Creature"
COMBAT_PASS: str = "Pass" 
COMBAT_ATTACK: str = "Attack with All"

#Actions
#DRAW_A_CARD: str = "Draw a Card"

#Replacement Effects
DECKING: str = "Decking"

##############
# Catalogs
##############
DECISION_EVENT_CATALOG: list[DecisionEvent] = [
        DecisionEvent(MAINPHASE, 0, [MAINPHASE_PASS, MAINPHASE_PLAY_CREATURE]),
        DecisionEvent(COMBAT, 0,[COMBAT_PASS, COMBAT_ATTACK])        
    ]

CARD_CATALOG: dict[int, CardInfo] = {
    1: CardInfo("Guy"),
    2: CardInfo("Land"),
    3: CardInfo("StrongGuy")
}
