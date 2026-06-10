from mtggympy.gameengine.cards.info import CardInfo
from mtggympy.gameengine.cards.catalog.lands import LAND_CATALOG
from mtggympy.gameengine.cards.catalog.creatures import CREATURE_CATALOG
from mtggympy.gameengine.constants import CardType

FULL_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG


def determine_card_type_from_name(name:str) -> CardType:
    try:
        return FULL_CATALOG[name].type
    except:
        return CardType.UNKNOWN