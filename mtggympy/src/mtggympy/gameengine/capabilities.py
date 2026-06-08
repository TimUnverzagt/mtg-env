from __future__ import annotations
from typing import Protocol, runtime_checkable
from abc import abstractmethod
from uuid import UUID
from mtggympy.gameengine.constants import Zone, ManaColor

@runtime_checkable
class Targetable(Protocol):
    @abstractmethod
    def allows_targeting_from_source(self, source: TargetSource) -> bool:
        raise NotImplementedError

@runtime_checkable
class TargetSource(Protocol):
    @abstractmethod
    def declare_target(self, intended_target: Targetable) -> None:
        raise NotImplementedError
    @abstractmethod
    def can_target(self, intended_target: Targetable) -> bool:
        raise NotImplementedError

@runtime_checkable
class ManaProvider(Protocol):
    @abstractmethod
    def is_ready(self) -> bool:
        raise NotImplementedError
    @abstractmethod
    def produce_mana(self) -> list[ManaColor]:
        raise NotImplementedError
    
@runtime_checkable
class ActiveGameElement(Protocol):
    @abstractmethod
    def get_id(self) -> UUID:
        raise NotImplementedError
    @abstractmethod
    def get_zone(self) -> Zone:
        raise NotImplementedError