from gameengine.gameobjects import CardInstance
from gameengine.constants import ManaColor, Zone
from gameengine.capabilities import ManaProvider

WASTES_NAME = "Wastes"

class Wastes(CardInstance, ManaProvider):

    def __init__(self, zone: Zone = Zone.LIBRARY) -> None:
        super().__init__(WASTES_NAME, zone)
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.COLORLESS]