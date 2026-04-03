from gameengine.cards.model.templates import CardInfo
from gameengine.cards.creatures import CREATURE_CATALOG
from gameengine.cards.lands import LAND_CATALOG

CARD_CATALOG: dict[str, CardInfo] = LAND_CATALOG | CREATURE_CATALOG