from mtggympy.gameengine.player import PlayerState, get_default_library
from mtggympy.gameengine.cards.logic.instances import CardInstance
from collections import defaultdict
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from mtggympy.gameengine.state import GameState
from mtggympy.gameengine.state.event import PlayerEvent

from mtggympy.app_config import STARTING_LIFE

def get_default_player(name: str) -> PlayerState:
    return PlayerState(
    name=name,
    current_life=STARTING_LIFE,
    cards_in_hand=[CardInstance(CreatureNames.ALPHA_MYR.value)],
    cards_in_library=get_default_library(),
    cards_in_play=[],
    death_description=None
)
def get_default_game_state() -> GameState:
    return GameState(
    halfturns_completed=0,
    active_player_index=0,
    game_over=False,
    player_states=[get_default_player("Alice"), get_default_player("Bob")],
    upcoming_event=PlayerEvent.DECLARE_ATTACKS,
    winner_positions=[],
    floating_mana=defaultdict(lambda: 0)
)