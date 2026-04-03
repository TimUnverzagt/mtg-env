from gameengine.cards.model.templates import CardInfo
from gameengine.cards.model.catalog import CARD_CATALOG
from gameengine.constants import Zone
from gameengine.capabilities import IActiveGameElement
from uuid import UUID, uuid4

class CardInstance(IActiveGameElement):
    def __init__(self, card_name: str, zone : Zone=Zone.LIBRARY) -> None:
        self.instance_id: UUID = uuid4()
        self.card_name: str = card_name
        self.zone: Zone = zone
        self.card_info: CardInfo = CARD_CATALOG[card_name]
        self.tapped: bool = False

    def get_id(self) -> UUID:
        return self.instance_id
    
    def get_zone(self) -> Zone:
        return self.zone

    def __str__(self, verbose: bool=False) -> str:
        if(verbose):
            return "[{}] {}".format(self.instance_id, str(self.card_info))
        else:
            return "[{}] {}".format(self.instance_id, self.card_info.name)