from gameengine.gameobjects import CardInstance
from gameengine.constants import ManaColor, Zone
from gameengine.capabilities import IManaProvider

class Wastes(CardInstance, IManaProvider):

    def __init__(self, card_name: str, zone: Zone = Zone.LIBRARY) -> None:
        super().__init__(card_name, zone)
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.COLORLESS]