from __future__ import annotations
from logging_config import env_log
import app_config as conf
from game.card import Card

from dataclasses import dataclass
from typing import Optional

    
def is_player_alive(info: PlayerInfo) -> bool:
        return info.death_description is None

class Player:
    def __init__(self, name: str) -> None:
        env_log.info("Setting up the new player {}".format(name))
        self.info: PlayerInfo = PlayerInfo(
            name = name,
            current_life = conf.STARTING_LIFE,
            cards_in_hand = [Card(1), Card(2), Card(1)],
            cards_in_library = conf.DECK_SIZE,
            death_description = None
        )

    def __str__(self) -> str:
        return "\n".join([
            str(self.info)
        ])
    
@dataclass
class PlayerInfo:
    name: str
    current_life: int 
    cards_in_hand: list[Card]
    cards_in_library: int
    death_description: Optional[str]

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand:",
            " | ".join(map(Card.__str__, self.cards_in_hand)),
            "Cards in Library: {}".format(self.cards_in_library)
        ])