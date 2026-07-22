from mtggympy.gameengine.cards.instances.types import CardInstance, LandInstance
from mtggympy.gameengine.constants import DeathDescription, ManaColor, GameStep
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
    death_description: Optional[DeathDescription]
    floating_mana: dict[ManaColor, int]
    additional_land_drops: int

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Library: {}".format(len(self.cards_in_library)),
            "Cards in Hand:",
            " | ".join(map(CardInstance.__str__, self.cards_in_hand)),
            "Lands in play:",
            " | ".join(map(CardInstance.__str__, filter(lambda card: isinstance(card, LandInstance),self.cards_in_play))),
            "Nonlands in play:",
            " | ".join(map(CardInstance.__str__, filter(lambda card: not isinstance(card, LandInstance),self.cards_in_play))),
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
