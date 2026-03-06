from gameengine.cards.model.templates import CardInfo, LandInfo
from gameengine.gameobjects import CardInstance
from gameengine.enums import ManaColor, Zone
from gameengine.capabilities import IManaProvider
from gameengine.state import GameState

LAND_CATALOG: list[CardInfo]

WASTES_INFO: LandInfo = LandInfo("Wastes")

class Wastes(CardInstance, IManaProvider):

    def __init__(self, card_id: int, zone: Zone = Zone.LIBRARY) -> None:
        super().__init__(card_id, zone)
    
    def is_ready(self) -> bool:
        return not self.tapped
    
    def produce_mana(self, state: GameState) -> GameState:
        self.tapped = True
        state.floating_mana[ManaColor.COLORLESS] += 1
        return state
