from mtggympy.gameengine.cards.catalog.info import SorceryInfo
from mtggympy.gameengine.cards.manacost import ManaCost
from mtggympy.gameengine.constants import ManaColor as MC
from enum import Enum
class SorceryNames(Enum):
    #White
    RELEASE_THE_DOGS = "release-the-dogs"
    #Blue
    DIVINATION = "divination"
    #Black
    INFEST = "infest"
    #Red
    BOLTWAVE = "boltwave"
    #Green
    EXPLORE = "explore"

SORCERY_CATALOG: dict[str, SorceryInfo] = {
    #White
    SorceryNames.RELEASE_THE_DOGS.value: SorceryInfo(SorceryNames.RELEASE_THE_DOGS.value, ManaCost({MC.WHITE: 1}, 3)),
    #Blue
    SorceryNames.DIVINATION.value: SorceryInfo(SorceryNames.DIVINATION.value, ManaCost({MC.BLUE: 1}, 2)),
    #Black
    SorceryNames.INFEST.value: SorceryInfo(SorceryNames.INFEST.value, ManaCost({MC.BLACK: 2}, 1)),
    #Red
    SorceryNames.BOLTWAVE.value: SorceryInfo(SorceryNames.BOLTWAVE.value, ManaCost({MC.RED: 1}, 0)),
    #Green
    SorceryNames.EXPLORE.value: SorceryInfo(SorceryNames.EXPLORE.value, ManaCost({MC.GREEN: 1}, 1))
}