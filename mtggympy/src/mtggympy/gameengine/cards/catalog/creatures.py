from mtggympy.gameengine.cards.catalog.info import CardInfo, CreatureInfo
from mtggympy.gameengine.cards.manacost import ManaCost
from mtggympy.gameengine.constants import ManaColor as MC
from enum import Enum

class CreatureNames(Enum):
    #Colorless
    METALLIC_SLIVER = "metallic-sliver"
    ALPHA_MYR = "alpha-myr"
    OMEGA_MYR = "omega-myr"
    SLIVER_CONSTRUCT =  "sliver-construct"
    GILDED_SENTINEL =  "gilded-sentinel"
    HEXPLATE_GOLEM =  "hexplate-golem"    
    #White
    #Blue
    #Black
    #Red
    GOBLIN_ASSAILANT = "goblin-assailant"
    GOBLIN_ROUGHRIDER = "goblin-roughrider"
    #Green
    BEAR_CUB = "bear-cub"
    BROODHUNTER_WURM = "broodhunter-wurm"
    #Multicolor
    RUINATION_WURM = "ruination-wurm"
    RHOX_BRUTE = "rhox-brute"

CREATURE_CATALOG: dict[str, CardInfo] = {
    #Colorless
    CreatureNames.METALLIC_SLIVER.value: CreatureInfo(CreatureNames.METALLIC_SLIVER.value, ManaCost({}, 1), 1, 1),
    CreatureNames.ALPHA_MYR.value: CreatureInfo(CreatureNames.ALPHA_MYR.value, ManaCost({}, 2), 2, 1),
    CreatureNames.OMEGA_MYR.value: CreatureInfo(CreatureNames.OMEGA_MYR.value, ManaCost({}, 2), 1, 2),
    CreatureNames.SLIVER_CONSTRUCT.value: CreatureInfo(CreatureNames.SLIVER_CONSTRUCT.value, ManaCost({}, 3), 2, 2),
    CreatureNames.GILDED_SENTINEL.value: CreatureInfo(CreatureNames.GILDED_SENTINEL.value, ManaCost({}, 4), 3, 3),
    CreatureNames.HEXPLATE_GOLEM.value: CreatureInfo(CreatureNames.HEXPLATE_GOLEM.value, ManaCost({}, 7), 5, 7),
    #White
    #Blue
    #Black
    #Red
    CreatureNames.GOBLIN_ASSAILANT.value: CreatureInfo(CreatureNames.GOBLIN_ASSAILANT.value, ManaCost({MC.RED: 1}, 1), 2, 2),
    CreatureNames.GOBLIN_ROUGHRIDER.value: CreatureInfo(CreatureNames.GOBLIN_ROUGHRIDER.value, ManaCost({MC.RED: 1}, 2), 3, 2),
    #Green
    CreatureNames.BEAR_CUB.value: CreatureInfo(CreatureNames.BEAR_CUB.value, ManaCost({MC.GREEN: 1}, 1), 2, 2),
    CreatureNames.BROODHUNTER_WURM.value: CreatureInfo(CreatureNames.BROODHUNTER_WURM.value, ManaCost({MC.GREEN: 1}, 3), 4, 3),
    #Multicolor
    CreatureNames.RHOX_BRUTE.value: CreatureInfo(CreatureNames.RHOX_BRUTE.value, ManaCost({MC.RED: 1, MC.GREEN: 1}, 2), 4, 4),
    CreatureNames.RUINATION_WURM.value: CreatureInfo(CreatureNames.RUINATION_WURM.value, ManaCost({MC.RED: 1, MC.GREEN: 1}, 4), 7, 6),
}
    
