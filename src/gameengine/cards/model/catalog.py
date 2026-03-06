from itertools import chain
from gameengine.cards.model.templates import CardInfo
from gameengine.cards.lands import LAND_CATALOG
from gameengine.cards.creatures import CREATURE_CATALOG

CARD_CATALOG: list[CardInfo] = list(chain.from_iterable([
    LAND_CATALOG,
    CREATURE_CATALOG
]))