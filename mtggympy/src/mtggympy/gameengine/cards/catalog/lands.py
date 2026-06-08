from mtggympy.gameengine.cards.info import CardInfo, LandInfo
from mtggympy.gameengine.cards.logic.basiclands import WASTES_NAME
from enum import Enum

class LandNames(Enum):
    WASTES = WASTES_NAME

LAND_CATALOG: dict[str, CardInfo] = {
    LandNames.WASTES.value: LandInfo(LandNames.WASTES.value)
}
