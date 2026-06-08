from mtggympy.gameengine.cards.info import CardInfo
from mtggympy.gameengine.cards.catalog.lands import LAND_CATALOG
from mtggympy.gameengine.cards.catalog.creatures import CREATURE_CATALOG

CARD_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG