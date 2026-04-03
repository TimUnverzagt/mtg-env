from typing import TypeVar, Generic
from abc import ABC, abstractmethod
from gameengine.priority.event import EventData
from gameengine.state import GameState

T = TypeVar("T")
    
class PriorityDecision(ABC, Generic[T]):
    def __init__(self, name: str, applicable_events: list[EventData]):
        self.name = name
        self.applicable_events = applicable_events
    
    @abstractmethod
    def resolve_decision_effects(self, gameState: GameState, options: T) -> GameState:
        raise NotImplementedError