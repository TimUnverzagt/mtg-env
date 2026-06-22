from mtggympy.gameengine.constants import GameStep
from mtggympy.gameengine.state.defaults import PlayerState, get_default_library
from mtggympy.gameengine.cards.logic.instances import generate_card_instance
from collections import defaultdict
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from mtggympy.gameengine.state.core import GameState

from mtggympy.app_config import STARTING_LIFE

def get_default_player(name: str) -> PlayerState:
    return PlayerState(
    name=name,
    current_life=STARTING_LIFE,
    cards_in_hand=[generate_card_instance(CreatureNames.ALPHA_MYR.value)],
    cards_in_library=get_default_library(),
    cards_in_play=[],
    death_description=None,
    floating_mana=defaultdict(lambda: 0)
)
def get_default_game_state() -> GameState:
    return GameState(
    halfturns_completed=0,
    active_player_index=0,
    game_over=False,
    step=GameStep.MAIN_1,
    player_states=[get_default_player("Alice"), get_default_player("Bob")],
    winner_positions=[],
    lands_played_this_turn=0
)