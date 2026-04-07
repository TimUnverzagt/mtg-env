from gameengine.cards.catalog.templates import CardInfo, LandInfo
from enum import Enum

class LandNames(Enum):
    WASTES = "Wastes"

LAND_CATALOG: dict[str, CardInfo] = {
    LandNames.WASTES.value: LandInfo(LandNames.WASTES.value)
}
