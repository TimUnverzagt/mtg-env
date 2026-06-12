from __future__ import annotations
import mtggympy.app_config as conf
from mtggympy.gameengine.state import PlayerState
from mtggympy.gameengine.gameobjects import CardInstance, generate_card_instance
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.app_config import DECK_SIZE
from collections import defaultdict

from mtggympy.logging_config import engine_log as logger

def get_default_library() -> list[CardInstance]:
    library: list[CardInstance] = []
    for i in range(0,DECK_SIZE):
        if (i % 3) >= 1:
            library.append(generate_card_instance(CreatureNames.ALPHA_MYR.value))
        else:
            library.append(generate_card_instance(LandNames.WASTES.value))
    return library

class Player:
    def __init__(self, name: str) -> None:
        logger.info("Setting up the new player {}".format(name))
        self.info: PlayerState = PlayerState(
            name = name,
            current_life = conf.STARTING_LIFE,
            cards_in_hand = [
                generate_card_instance(CreatureNames.ALPHA_MYR.value),
                generate_card_instance(LandNames.WASTES.value),
                generate_card_instance(LandNames.WASTES.value)],
            cards_in_play=[],
            cards_in_library = get_default_library(),
            death_description = None,
            floating_mana=defaultdict(lambda: 0)
        )

    def __str__(self) -> str:
        return "\n".join([
            str(self.info)
        ])