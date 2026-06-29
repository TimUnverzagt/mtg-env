
from mtggympy.gameengine.cards.catalog.info import LandInfo
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.cards.instances.capabilities import ManaProvider
from mtggympy.gameengine.cards.instances.types import LandInstance
from mtggympy.gameengine.constants import ManaColor


class WastesInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.WASTES.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.COLORLESS]
    
class PlainsInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.PLAINS.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.WHITE]


class IslandInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.ISLAND.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.BLUE]


class SwampInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.SWAMP.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.BLACK]
    

class MountainInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.MOUNTAIN.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.RED]

class ForestInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.FOREST.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.GREEN]
