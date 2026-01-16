from __future__ import annotations
import game.constants as const
class DecisionEvent:

    def __init__(self, name: str, neutral_action_index: int, possible_actions: list [str]) -> None:
        self.name: str = name
        self.neutral_action_index: int = neutral_action_index
        self.possible_actions: list [str] =  possible_actions

    def __str__(self) -> str:
        return "{}: <{}>".format(self.name, ",".join(self.possible_actions))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DecisionEvent):
            return False
        return self.name == other.name
    

DECISION_EVENT_CATALOG: list[DecisionEvent] = [
    DecisionEvent(const.MAINPHASE, 0, [const.MAINPHASE_PASS, const.MAINPHASE_PLAY_CREATURE]),
    DecisionEvent(const.COMBAT, 0,[const.COMBAT_PASS, const.COMBAT_ATTACK])        
]