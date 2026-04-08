from gameengine.state import GameState
from gameengine.priority.event import PlayerEvent
from gameengine.constants import Action
from gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
import gameengine.core as Engine
from tests.default_data import get_default_game_state


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

