from __future__ import annotations
import numpy as np
from mtggympy.gameengine.constants import Phase
from enum import Enum
from dataclasses import dataclass

@dataclass
class ActionArgumentType:
    name: str
    dimensionality: int
    expects_collection: bool
    
class ActionData(Enum):
    PASS = ActionArgumentType("pass", 0, False)
    ACTIVATE_LANDS = ActionArgumentType("activate_lands", 1, True)
    PLAY_CARD = ActionArgumentType("play_card", 1, False)
    ATTACK = ActionArgumentType("attack", 1, True)
    BLOCK = ActionArgumentType("block", 2, True)

@dataclass
class ActionIntent:
    action: ActionData
    parameters: np.ndarray | None


@dataclass
class EventData:
    applicable_phase: Phase
    neutral_action_index: int
    possible_actions: list[ActionData]

    def __str__(self) -> str:
        return "{}: <{}>".format(self.applicable_phase, ",".join(str(self.possible_actions)))
    

class PlayerEvent(Enum):
    MAIN_PHASE_EMPTY_STACK = EventData(Phase.MAINPHASE, 0, [ActionData.PASS, ActionData.PLAY_CARD, ActionData.ACTIVATE_LANDS])
    DECLARE_ATTACKS = EventData(Phase.COMBAT, 0, [ActionData.PASS, ActionData.ATTACK]) 


