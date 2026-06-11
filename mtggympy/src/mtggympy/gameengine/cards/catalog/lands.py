from mtggympy.gameengine.cards.info import CardInfo, LandInfo
from enum import Enum

class LandNames(Enum):
    WASTES = "wastes"

LAND_CATALOG: dict[str, CardInfo] = {
    LandNames.WASTES.value: LandInfo(LandNames.WASTES.value)
}
