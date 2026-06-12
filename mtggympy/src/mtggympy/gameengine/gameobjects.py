from mtggympy.gameengine.cards.info import CardInfo, CreatureInfo, LandInfo, SpellInfo
from mtggympy.gameengine.constants import ManaColor
from mtggympy.gameengine.capabilities import ActiveGameElement
from mtggympy.gameengine.constants import CardType
import mtggympy.gameengine.cards.catalog.lookup as lookup
from mtggympy.gameengine.cards.catalog.lands import LandNames
from mtggympy.gameengine.constants import ManaColor
from mtggympy.gameengine.capabilities import ManaProvider
from uuid import UUID, uuid4

from mtggympy.logging_config import engine_log as logger

class CardInstance(ActiveGameElement):
    def __init__(self, info: CardInfo) -> None:
        self.instance_id: UUID = uuid4()
        self.card_name: str = info.name
        self.tapped: bool = False            
        self.type: CardType = info.type

    def get_id(self) -> UUID:
        return self.instance_id

    def __str__(self, verbose: bool=False) -> str:
        return "[{}] {}".format(self.instance_id, self.card_name)
    
class SpellInstance(CardInstance):
    def __init__(self, info: SpellInfo) -> None:
        super().__init__(info)
        self.mana_cost = info.mana_cost

class LandInstance(CardInstance):
    def __init__(self, info: LandInfo) -> None:
        super().__init__(info)

class CreatureInstance(SpellInstance):
    def __init__(self, info: CreatureInfo) -> None:
        super().__init__(info)
        self.power: int = info.power
        self.toughness: int = info.toughness
        self.summoning_sick: bool = False

class WastesInstance(LandInstance, ManaProvider):
    def __init__(self) -> None:
        super().__init__(LandInfo(LandNames.WASTES.value))
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self) -> list[ManaColor]:
        self.tapped = True
        return [ManaColor.COLORLESS]
    
def generate_card_instance(card_name: str) -> CardInstance:
    info: CardInfo | None =  lookup.card_info(card_name)
    if info is None:
        logger.error("Could not instatiate card for name \"{}\"".format(card_name))
        raise Exception
    if card_name == LandNames.WASTES.value:
        return WastesInstance()
    if isinstance(info, CreatureInfo):
        return CreatureInstance(info)
    if isinstance(info, LandInfo):
        return LandInstance(info)
    return CardInstance(info)
