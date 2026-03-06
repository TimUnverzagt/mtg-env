from __future__ import annotations
from typing import TypeVar, Generic
from abc import ABC, abstractmethod
from gameengine.enums import Phase, Action
from gameengine.state import GameState



class PriorityEvent:
    def __init__(self, applicable_phase: Phase, neutral_action_index: int, possible_actions: list [Action]) -> None:
        self.applicable_phase: Phase = applicable_phase
        self.neutral_action_index: int = neutral_action_index
        self.possible_actions: list[Action] =  possible_actions

    def __str__(self) -> str:
        return "{}: <{}>".format(self.applicable_phase, ",".join(str(self.possible_actions)))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriorityEvent):
            return False
        return self.applicable_phase == other.applicable_phase
    

T = TypeVar("T")

class PriorityDecision(ABC, Generic[T]):
    def __init__(self, name: str, applicable_events: list[PriorityEvent]):
        self.name = name
        self.applicable_events = applicable_events
    
    @abstractmethod
    def resolve_decision_effects(self, gameState: GameState, options: T) -> GameState:
        raise NotImplementedError
    

DECISION_EVENT_CATALOG: list[PriorityEvent] = [
    PriorityEvent(Phase.MAINPHASE, 0, [Action.PASS, Action.PLAY_CARD]),
    PriorityEvent(Phase.COMBAT, 0,[Action.PASS, Action.ATTACK])        
]