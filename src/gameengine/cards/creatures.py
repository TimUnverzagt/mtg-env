from gameengine.cards.model.templates import CardInfo, CreatureInfo

METALLIC_SLIVER_INFO = CreatureInfo("Metallic Sliver", 1, 1, 1)
ALPHA_MYR_INFO = CreatureInfo("Alpha Myr", 2, 2, 1)
OMEGA_MYR_INFO = CreatureInfo("Omega Myr", 2, 1, 2)
SLIVER_CONSTRUCT_INFO = CreatureInfo("Sliver Construct", 3, 2, 2)

CREATURE_CATALOG: list[CardInfo] = [
    METALLIC_SLIVER_INFO,
    ALPHA_MYR_INFO,
    OMEGA_MYR_INFO,
    SLIVER_CONSTRUCT_INFO
]
    
