from gameengine.player import PlayerInfo, get_default_library
from gameengine.gameobjects import CardInstance
from collections import defaultdict
from gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from gameengine.state import GameState
from gameengine.priority.event import PlayerEvent

from config.app_config import STARTING_LIFE

def get_default_player(name: str) -> PlayerInfo:
    return PlayerInfo(
    name=name,
    current_life=STARTING_LIFE,
    cards_in_hand=[CardInstance(CreatureNames.ALPHA_MYR.value)],
    cards_in_library=get_default_library(),
    cards_in_play=[],
    death_description=None
)
def get_default_game_state() -> GameState:
    return GameState(
    player_turns_completed=0,
    active_player_index=0,
    game_over=False,
    player_infos=[get_default_player("Alice"), get_default_player("Bob")],
    upcoming_event=PlayerEvent.DECLARE_ATTACKS,
    winner_positions=[],
    floating_mana=defaultdict(lambda: 0)
)