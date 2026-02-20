from __future__ import annotations
from typing import TypeVar, Generic
from abc import ABC, abstractmethod
import gameengine.constants as const
from gameengine.state import GameState



class PriorityEvent:
    def __init__(self, name: str, neutral_action_index: int, possible_actions: list [str]) -> None:
        self.name: str = name
        self.neutral_action_index: int = neutral_action_index
        self.possible_actions: list [str] =  possible_actions

    def __str__(self) -> str:
        return "{}: <{}>".format(self.name, ",".join(self.possible_actions))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriorityEvent):
            return False
        return self.name == other.name
    

T = TypeVar("T")

class PriorityDecision(ABC, Generic[T]):
    def __init__(self, name: str, applicable_events: list[PriorityEvent]):
        self.name = name
        self.applicable_events = applicable_events
    
    @abstractmethod
    def resolve_decision_effects(self, gameState: GameState, options: T) -> GameState:
        raise NotImplementedError
    

DECISION_EVENT_CATALOG: list[PriorityEvent] = [
    PriorityEvent(const.MAINPHASE, 0, [const.MAINPHASE_PASS, const.MAINPHASE_PLAY_CREATURE]),
    PriorityEvent(const.COMBAT, 0,[const.COMBAT_PASS, const.COMBAT_ATTACK])        
]