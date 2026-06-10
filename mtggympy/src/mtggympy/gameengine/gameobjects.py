from mtggympy.gameengine.constants import Zone
from mtggympy.gameengine.capabilities import ActiveGameElement
from mtggympy.gameengine.constants import CardType
from uuid import UUID, uuid4

class CardInstance(ActiveGameElement):
    def __init__(self, card_name: str, zone : Zone=Zone.LIBRARY) -> None:
        self.instance_id: UUID = uuid4()
        self.card_name: str = card_name
        self.zone: Zone = zone
        self.tapped: bool = False
        self.type: CardType = CardType.UNKNOWN

    def get_id(self) -> UUID:
        return self.instance_id
    
    def get_zone(self) -> Zone:
        return self.zone

    def __str__(self, verbose: bool=False) -> str:
        return "[{}] {}".format(self.instance_id, self.card_name)