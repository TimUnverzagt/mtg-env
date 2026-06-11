from mtggympy.gameengine.cards.info import CardInfo, SpellInfo
from mtggympy.gameengine.cards.catalog.lands import LAND_CATALOG
from mtggympy.gameengine.cards.catalog.creatures import CREATURE_CATALOG
from mtggympy.gameengine.constants import CardType, ManaColor

FULL_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG


def card_type(name:str) -> CardType:
    try:
        return FULL_CATALOG[name].type
    except:
        return CardType.UNKNOWN

def mana_cost(name:str) -> dict[ManaColor, int]|None:
    info: CardInfo
    try:
        info = FULL_CATALOG[name]
    except:
        return None
    if not isinstance(info, SpellInfo):
        return None
    return info.mana_cost