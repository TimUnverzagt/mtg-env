from mtggympy.gameengine.cards.catalog.sorceries import SorceryNames, SORCERY_CATALOG
from mtggympy.gameengine.cards.instances.capabilities import ResolutionEffect
from mtggympy.gameengine.cards.instances.types import SorceryInstance
from mtggympy.gameengine.state.core import GameState, PlayerState
import mtggympy.gameengine.core as GameEngine


class ExploreInstance(SorceryInstance, ResolutionEffect):
    def __init__(self) -> None:
        super().__init__(SORCERY_CATALOG[SorceryNames.EXPLORE.value])
    
    def resolve(self, game_state: GameState, owning_seat: int) -> None:
        owner_state: PlayerState = game_state.player_states[owning_seat]
        owner_state.additional_land_drops += 1
        GameEngine.execute_action(owning_seat, game_state, GameEngine.draw_card)
