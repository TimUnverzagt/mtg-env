from __future__ import annotations
import mtggympy.config.app_config as conf
from mtggympy.gameengine.state.core import PlayerState
from collections import defaultdict
import mtggympy.config.decks as decks

from mtggympy.config.logging_config import engine_log as logger

class Player:
    def __init__(self, name: str) -> None:
        logger.info("Setting up the new player {}".format(name))
        self.info: PlayerState = PlayerState(
            name = name,
            current_life = conf.STARTING_LIFE,
            cards_in_hand = [],
            cards_in_play=[],
            cards_in_library = decks.get_fourty_card_red_green(),
            death_description = None,
            floating_mana=defaultdict(lambda: 0),
            additional_land_drops=0
        )

    def __str__(self) -> str:
        return "\n".join([
            str(self.info)
        ])