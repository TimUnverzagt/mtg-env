from mtggympy.gameengine.cards.catalog.info import CardInfo, CreatureInfo, LandInfo, SpellInfo, SorceryInfo
from mtggympy.gameengine.cards.instances.capabilities import ActiveGameElement
from mtggympy.gameengine.cards.manacost import ManaCost
from uuid import UUID, uuid4

from mtggympy.gameengine.constants import CardType

#from mtggympy.logging_config import engine_log as logger

class CardInstance(ActiveGameElement):
    def __init__(self, info: CardInfo) -> None:
        self.instance_id: UUID = uuid4()
        self.card_name: str = info.name
        self.tapped: bool = False
        self.type: CardType = info.type     

    def get_id(self) -> UUID:
        return self.instance_id

    def __str__(self, verbose: bool=False) -> str:
        return "{}({})".format(self.card_name, self.instance_id)
    
class SpellInstance(CardInstance):
    def __init__(self, info: SpellInfo) -> None:
        super().__init__(info)
        self.mana_cost: ManaCost = info.mana_cost

class SorceryInstance(SpellInstance):
    def __init__(self, info: SorceryInfo) -> None:
        super().__init__(info)

class LandInstance(CardInstance):
    def __init__(self, info: LandInfo) -> None:
        super().__init__(info)

class CreatureInstance(SpellInstance):
    def __init__(self, info: CreatureInfo) -> None:
        super().__init__(info)
        self.power: int = info.power
        self.toughness: int = info.toughness
        self.summoning_sick: bool = False
        self.attacking: bool = False
        self.marked_damage: int = 0
    
