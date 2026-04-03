from gameengine.cards.model.templates import CardInfo, CreatureInfo
from enum import Enum

class Names(Enum):
    METALLIC_SLIVER = "Metallic Sliver"
    ALPHA_MYR = "Alpha Myr"
    OMEGA_MYR = "Omega Myr"
    SLIVER_CONSTRUCT =  "Sliver Construct"

CREATURE_CATALOG: dict[str, CardInfo] = {
    Names.METALLIC_SLIVER.value: CreatureInfo(Names.METALLIC_SLIVER.value, 1, 1, 1),
    Names.ALPHA_MYR.value: CreatureInfo(Names.ALPHA_MYR.value, 2, 2, 1),
    Names.OMEGA_MYR.value: CreatureInfo(Names.OMEGA_MYR.value, 2, 1, 2),
    Names.SLIVER_CONSTRUCT.value: CreatureInfo(Names.SLIVER_CONSTRUCT.value, 3, 2, 2)
}
    
