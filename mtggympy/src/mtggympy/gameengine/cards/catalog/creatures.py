from mtggympy.gameengine.cards.info import CardInfo, CreatureInfo
from mtggympy.gameengine.constants import ManaColor as MC
from enum import Enum

class CreatureNames(Enum):
    METALLIC_SLIVER = "metallic-sliver"
    ALPHA_MYR = "alpha-myr"
    OMEGA_MYR = "omega-myr"
    SLIVER_CONSTRUCT =  "sliver-construct"

CREATURE_CATALOG: dict[str, CardInfo] = {
    CreatureNames.METALLIC_SLIVER.value: CreatureInfo(CreatureNames.METALLIC_SLIVER.value, {MC.COLORLESS: 1}, 1, 1),
    CreatureNames.ALPHA_MYR.value: CreatureInfo(CreatureNames.ALPHA_MYR.value, {MC.COLORLESS: 2}, 2, 1),
    CreatureNames.OMEGA_MYR.value: CreatureInfo(CreatureNames.OMEGA_MYR.value, {MC.COLORLESS: 2}, 1, 2),
    CreatureNames.SLIVER_CONSTRUCT.value: CreatureInfo(CreatureNames.SLIVER_CONSTRUCT.value, {MC.COLORLESS: 3}, 2, 2)
}
    
