from gameengine.state import GameState
from gameengine.player import PlayerInfo, get_default_library
from gameengine.gameobjects import CardInstance
from gameengine.priority.event import PlayerEvent
from gameengine.constants import Action
from gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
import gameengine.core as Engine
from collections import defaultdict

def get_default_player(name: str) -> PlayerInfo:
    return PlayerInfo(
    name=name,
    current_life=5,
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

class TestGameEngine():

    def test_refusal_of_invalid_intent(self):
        #Setup
        game_state: GameState = get_default_game_state()

        #Execute
        Engine.step(acting_seat=0, decision_intent=Action.PLAY_CARD, game_state=game_state)

        #Assert
        assert game_state.upcoming_event == PlayerEvent.DECLARE_ATTACKS

    def test_attack_decision(self):
        #Setup 
        game_state: GameState = get_default_game_state()

        #Execute
        Engine.handle_combat_decision(0, Action.ATTACK, game_state)

        #Assert
        assert game_state.upcoming_event == PlayerEvent.MAIN_PHASE_EMPTY_STACK
        assert game_state.player_infos[1].current_life == 4


    def test_drawing_a_card(self):
        #Setup
        game_state: GameState = get_default_game_state()

        #Execute:
        Engine.execute_action(0, game_state, Engine.draw_card)

        #Assert
        assert len(game_state.player_infos[0].cards_in_hand) == len(get_default_game_state().player_infos[0].cards_in_hand) + 1
        assert len(game_state.player_infos[0].cards_in_library) == len(get_default_game_state().player_infos[0].cards_in_library) - 1

    def test_decking(self):
        #Setup
        game_state: GameState = get_default_game_state()
        game_state.player_infos[0].cards_in_library = []

        #Execute        
        Engine.execute_action(0, game_state, Engine.draw_card)

        #Assert
        assert game_state.game_over == True
        assert 1 in game_state.winner_positions

