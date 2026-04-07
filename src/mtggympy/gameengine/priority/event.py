from __future__ import annotations
from gameengine.constants import Phase, Action
from enum import Enum
from dataclasses import dataclass

@dataclass
class EventData:
    applicable_phase: Phase
    neutral_action_index: int
    possible_actions: list[Action]

    def __str__(self) -> str:
        return "{}: <{}>".format(self.applicable_phase, ",".join(str(self.possible_actions)))
    

class PlayerEvent(Enum):
    MAIN_PHASE_EMPTY_STACK = EventData(Phase.MAINPHASE, 0, [Action.PASS, Action.PLAY_CARD, Action.ACTIVATE_LANDS])
    DECLARE_ATTACKS = EventData(Phase.COMBAT, 0, [Action.PASS, Action.ATTACK]) 


