from mtggympy.gameengine.constants import ManaColor, Zone
from mtggympy.gameengine.capabilities import ActiveGameElement
from mtggympy.gameengine.constants import CardType
import mtggympy.gameengine.cards.catalog.lookup as lookup
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.constants import ManaColor, Zone
from mtggympy.gameengine.capabilities import ManaProvider
from uuid import UUID, uuid4

class CardInstance(ActiveGameElement):
    def __init__(self, card_name: str, zone : Zone=Zone.LIBRARY) -> None:
        self.instance_id: UUID = uuid4()
        self.card_name: str = card_name
        self.zone: Zone = zone
        self.tapped: bool = False            
        self.type: CardType = lookup.card_type(card_name)
        self.mana_cost: dict[ManaColor, int]|None = lookup.mana_cost(card_name)


    def get_id(self) -> UUID:
        return self.instance_id
    
    def get_zone(self) -> Zone:
        return self.zone

    def __str__(self, verbose: bool=False) -> str:
        return "[{}] {}".format(self.instance_id, self.card_name)
    

class WastesInstance(CardInstance, ManaProvider):

    def __init__(self, zone: Zone = Zone.LIBRARY) -> None:
        super().__init__(LandNames.WASTES.value, zone)
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.COLORLESS]