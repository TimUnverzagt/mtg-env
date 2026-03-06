from __future__ import annotations
from typing import Protocol
from abc import abstractmethod
from uuid import UUID
from gameengine.state import GameState
from gameengine.enums import Zone

class ITargetable(Protocol):
    @abstractmethod
    def allows_targeting_from_source(self, source: ITargetSource) -> bool:
        raise NotImplementedError

class ITargetSource(Protocol):
    @abstractmethod
    def declare_target(self, intended_target: ITargetable) -> None:
        raise NotImplementedError
    @abstractmethod
    def can_target(self, intended_target: ITargetable) -> bool:
        raise NotImplementedError

class IManaProvider(Protocol):
    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError
    @abstractmethod
    def produce_mana(self, state: GameState) -> GameState:
        raise NotImplementedError
    
class IActiveGameElement(Protocol):
    @abstractmethod
    def get_id(self) -> UUID:
        raise NotImplementedError
    @abstractmethod
    def get_zone(self) -> Zone:
        raise NotImplementedError