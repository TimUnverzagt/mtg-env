from gameengine.cards.model.templates import CardInfo, LandInfo
from enum import Enum
from gameengine.gameobjects import CardInstance
from gameengine.constants import ManaColor, Zone
from gameengine.capabilities import IManaProvider
from gameengine.state import GameState

class Name(Enum):
    WASTES = "Wastes"

LAND_CATALOG: dict[str, CardInfo] = {
    Name.WASTES.value: LandInfo(Name.WASTES.value)
}

class Wastes(CardInstance, IManaProvider):

    def __init__(self, card_name: str, zone: Zone = Zone.LIBRARY) -> None:
        super().__init__(card_name, zone)
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self, state: GameState) -> GameState:
        self.tapped = True
        state.floating_mana[ManaColor.COLORLESS] += 1
        return state
