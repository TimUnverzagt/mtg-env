from gameengine.cards.info import CardInfo
from gameengine.cards.catalog.lands import LAND_CATALOG
from gameengine.cards.catalog.creatures import CREATURE_CATALOG

CARD_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG