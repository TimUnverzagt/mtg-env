from dataclasses import dataclass

from mtggympy.gameengine.constants import GameStep, ManaColor
from mtggympy.gameengine.gameobjects import CardInstance
from mtggympy.gameengine.priority.event import PlayerEvent

@dataclass
class ObservedSelfState:
    name: str
    current_life: int 
    cards_in_library: int
    cards_in_hand: list[CardInstance]
    cards_in_play: list[CardInstance]
    floating_mana: dict[ManaColor, int]

@dataclass
class ObservedOpponentState:
    name: str
    current_life: int 
    cards_in_library: int
    cards_in_hand: int
    cards_in_play: list[CardInstance]
    floating_mana: dict[ManaColor, int]

@dataclass
class ObservedGameState:
    name_of_active_player: str
    halfturns_completed: int
    self_is_active_player: bool
    step: GameStep
    event: PlayerEvent
    self_state: ObservedSelfState
    opponent_states: list[ObservedOpponentState]
    lands_played_this_turn: int


