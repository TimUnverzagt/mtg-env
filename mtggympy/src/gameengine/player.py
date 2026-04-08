from __future__ import annotations
import app_config as conf
from gameengine.gameobjects import CardInstance
from gameengine.cards.catalog.creatures import CreatureNames
from gameengine.cards.catalog.lands import LandNames

from dataclasses import dataclass
from typing import Optional


from logging_config import engine_log as logger

    
def is_player_alive(info: PlayerInfo) -> bool:
        return info.death_description is None

class Player:
    def __init__(self, name: str) -> None:
        logger.info("Setting up the new player {}".format(name))
        self.info: PlayerInfo = PlayerInfo(
            name = name,
            current_life = conf.STARTING_LIFE,
            cards_in_hand = [
                 CardInstance(CreatureNames.ALPHA_MYR.value),
                 CardInstance(LandNames.WASTES.value),
                 CardInstance(LandNames.WASTES.value)],
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
    cards_in_hand: list[CardInstance]
    cards_in_library: int
    death_description: Optional[str]

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand:",
            " | ".join(map(CardInstance.__str__, self.cards_in_hand)),
            "Cards in Library: {}".format(self.cards_in_library)
        ])