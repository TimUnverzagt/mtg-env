from mtggympy.gameengine.cards.catalog.info import CardInfo, LandInfo
from enum import Enum

class LandNames(Enum):
    WASTES = "wastes"
    PLAINS = "plains"
    ISLAND = "island"
    SWAMP = "swamp"
    MOUNTAIN = "mountain"
    FOREST = "forest"

LAND_CATALOG: dict[str, CardInfo] = {
    LandNames.WASTES.value: LandInfo(LandNames.WASTES.value),
    LandNames.PLAINS.value: LandInfo(LandNames.PLAINS.value),
    LandNames.ISLAND.value: LandInfo(LandNames.ISLAND.value),
    LandNames.SWAMP.value: LandInfo(LandNames.SWAMP.value),
    LandNames.MOUNTAIN.value: LandInfo(LandNames.MOUNTAIN.value),
    LandNames.FOREST.value: LandInfo(LandNames.FOREST.value)
}
