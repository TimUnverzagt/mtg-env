from mtggympy.gameengine.cards.catalog.info import CardInfo, SpellInfo, CreatureInfo
from mtggympy.gameengine.cards.catalog.lands import LAND_CATALOG
from mtggympy.gameengine.cards.catalog.creatures import CREATURE_CATALOG
from mtggympy.gameengine.cards.catalog.sorceries import SORCERY_CATALOG
from mtggympy.gameengine.cards.manacost import ManaCost
from mtggympy.gameengine.constants import CardType

FACEDOWN_CARD_NAME = "facedown"

FULL_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG | SORCERY_CATALOG
FULL_CATALOG[FACEDOWN_CARD_NAME] = CardInfo(FACEDOWN_CARD_NAME)

def card_info(name:str) -> CardInfo | None:
    try:
        return FULL_CATALOG[name]
    except:
        return None

def card_type(name:str) -> CardType:
    try:
        return FULL_CATALOG[name].type
    except:
        return CardType.UNKNOWN

def mana_cost(name:str) -> ManaCost | None:
    info: CardInfo
    try:
        info = FULL_CATALOG[name]
    except:
        return None
    if not isinstance(info, SpellInfo):
        return None
    return info.mana_cost

def power_toughness(name:str) -> tuple[int,int] | None:
    info: CardInfo
    try:
        info = FULL_CATALOG[name]
    except:
        return None
    if not isinstance(info, CreatureInfo):
        return None
    return (info.power, info.toughness)