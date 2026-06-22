from __future__ import annotations
import mtggympy.app_config as conf
from mtggympy.gameengine.state.core import PlayerState
from mtggympy.gameengine.cards.logic.instances import CardInstance, generate_card_instance
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

def get_fourty_card_library() -> list[CardInstance]:
    library: list[CardInstance] = []
    for i in range(0, 40):
        if i in range(0,18):
            library.append(generate_card_instance(LandNames.WASTES.value))
        if i in range(18,22):
            library.append(generate_card_instance(CreatureNames.ALPHA_MYR.value))
        if i in range(22,26):
            library.append(generate_card_instance(CreatureNames.METALLIC_SLIVER.value))
        if i in range(26,30):
            library.append(generate_card_instance(CreatureNames.OMEGA_MYR.value))
        if i in range(30,34):
            library.append(generate_card_instance(CreatureNames.SLIVER_CONSTRUCT.value))
        if i in range(34,38):
            library.append(generate_card_instance(CreatureNames.GILDED_SENTINEL.value))
        if i in range(38,40):
            library.append(generate_card_instance(CreatureNames.HEXPLATE_GOLEM.value))
    return library

class Player:
    def __init__(self, name: str) -> None:
        logger.info("Setting up the new player {}".format(name))
        self.info: PlayerState = PlayerState(
            name = name,
            current_life = conf.STARTING_LIFE,
            cards_in_hand = [],
            cards_in_play=[],
            cards_in_library = get_fourty_card_library(),
            death_description = None,
            floating_mana=defaultdict(lambda: 0)
        )

    def __str__(self) -> str:
        return "\n".join([
            str(self.info)
        ])