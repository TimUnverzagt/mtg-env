from __future__ import annotations
import numpy as np
from mtggympy.gameengine.constants import GameStep
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
    name: str
    neutral_action_index: int
    possible_actions: list[ActionData]

    def __str__(self) -> str:
        return "{}: <{}>".format(self.name, ",".join(str(self.possible_actions)))

class PlayerEvent(Enum):
    MAINPHASE_EMPTY_STACK = EventData("MP:EmptyStack", 0, [ActionData.PASS, ActionData.PLAY_CARD, ActionData.ACTIVATE_LANDS])
    DECLARE_ATTACKS = EventData("COM:DeclareAttacks", 0, [ActionData.PASS, ActionData.ATTACK])
    DECLARE_BLOCKS = EventData("COM:DeclareBlocks", 0, [ActionData.PASS, ActionData.BLOCK])
    NO_OP = EventData("Default:NoOp", 0, [ActionData.PASS]) 

def event_from_step(step: GameStep) -> PlayerEvent:
    match step:
        case GameStep.MAIN_1 | GameStep.MAIN_2:
            return PlayerEvent.MAINPHASE_EMPTY_STACK
        case GameStep.ATTACK_STEP:
            return PlayerEvent.DECLARE_ATTACKS
        case GameStep.BLOCK_STEP:
            return PlayerEvent.DECLARE_BLOCKS
        case _:
            return PlayerEvent.NO_OP


