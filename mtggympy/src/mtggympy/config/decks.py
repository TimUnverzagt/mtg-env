

from enum import Enum

from mtggympy.gameengine.cards.catalog.creatures import CreatureNames
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.cards.catalog.sorceries import SorceryNames
from mtggympy.gameengine.cards.instances.types import CardInstance
from mtggympy.gameengine.cards.instances.factory import generate_card_instance

DECK_SIZE: int = 40
class DeckName(Enum):
    GENERATED = "generated"
    COLORLESS = "colorless"
    RED_GREEN = "red-green"

def produce_deck(deck_name: DeckName) -> list[CardInstance]:
    match deck_name:
        case DeckName.GENERATED:
            return get_default_library(DECK_SIZE)
        case DeckName.COLORLESS:
            return get_fourty_card_colorless()
        case DeckName.RED_GREEN:
            return get_fourty_card_red_green()

def get_default_library(deck_size: int) -> list[CardInstance]:
    library: list[CardInstance] = []
    for i in range(0,deck_size):
        if (i % 3) >= 1:
            library.append(generate_card_instance(CreatureNames.ALPHA_MYR.value))
        else:
            library.append(generate_card_instance(LandNames.WASTES.value))
    return library

def get_fourty_card_colorless() -> list[CardInstance]:
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

def get_fourty_card_red_green() -> list[CardInstance]:
    library: list[CardInstance] = []
    for i in range(0, 40):
        if i in range(0,9):
            library.append(generate_card_instance(LandNames.MOUNTAIN.value))
        if i in range(10,18):
            library.append(generate_card_instance(LandNames.FOREST.value))
        if i in range(18,22):
            library.append(generate_card_instance(CreatureNames.GOBLIN_ASSAILANT.value))
        if i in range(22,26):
            library.append(generate_card_instance(CreatureNames.GOBLIN_ROUGHRIDER.value))
        if i in range(26,30):
            library.append(generate_card_instance(CreatureNames.BEAR_CUB.value))
        if i in range(30,33):
            library.append(generate_card_instance(CreatureNames.BROODHUNTER_WURM.value))
        if i in range(33,35):
            library.append(generate_card_instance(SorceryNames.EXPLORE.value))
        if i in range(35,38):
            library.append(generate_card_instance(CreatureNames.RHOX_BRUTE.value))
        if i in range(38,40):
            library.append(generate_card_instance(CreatureNames.RUINATION_WURM.value))
    return library

