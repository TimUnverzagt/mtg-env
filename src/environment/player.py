from environment.card import Card
from logging_config import env_log

import app_config as conf

class Player:

    def __init__(self, name: str) -> None:
        env_log.info("Setting up the new player {}".format(name))
        self.name: str = name
        self.current_life: int = conf.STARTING_LIFE
        self.cards_in_hand: list[Card] = [Card(1), Card(2), Card(1)]
        self.cards_in_library: int = conf.DECK_SIZE
        self.death_description: str | None = None

    def __str__(self) -> str:
        return "\n".join([
            "Name: {}".format(self.name),
            "Current Life: {}".format(self.current_life),
            "Cards in Hand:",
            " | ".join(map(Card.__str__, self.cards_in_hand)),
            "Cards in Library: {}".format(self.cards_in_library)
        ])
    
    def is_alive(self) -> bool:
        return self.death_description is None