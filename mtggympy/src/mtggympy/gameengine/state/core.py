from mtggympy.gameengine.cards.instances.types import CardInstance
from mtggympy.gameengine.constants import ManaColor, GameStep
from mtggympy.gameengine.constants import ManaColor
from dataclasses import dataclass
from typing import Optional

@dataclass
class PlayerState:
    name: str
    current_life: int 
    cards_in_hand: list[CardInstance]
    cards_in_play: list[CardInstance]
    cards_in_library: list[CardInstance]
    death_description: Optional[str]
    floating_mana: dict[ManaColor, int]

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand:",
            " | ".join(map(CardInstance.__str__, self.cards_in_hand)),
            "Cards in Library: {}".format(len(self.cards_in_library))
        ])

@dataclass
class GameState:
    halfturns_completed: int
    active_player_index: int
    game_over: bool
    step: GameStep
    player_states: list[PlayerState]
    winner_positions: list[int]
    lands_played_this_turn: int

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Active Player Index: {}".format(self.active_player_index),
            "---------------------------------------------",
            "Completed Halfturns: {}".format(self.halfturns_completed),
            "Upcoming Event: {}".format(self.step.name),
            "Active Player Index: {}".format(self.active_player_index),
            "Game over: {}".format(self.game_over),
            "---------------------------------------------",
            "Player 0:",
            str(self.player_states[0]),
            "---------------------------------------------",
            "Player 1:",
            str(self.player_states[1]),
            "---------------------------------------------"
        ])
    
def is_player_alive(info: PlayerState) -> bool:
        return info.death_description is None
