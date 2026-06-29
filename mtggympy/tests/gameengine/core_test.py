from mtggympy.gameengine.state.core import GameState
from mtggympy.gameengine.state.event import PlayerEvent
from mtggympy.gameengine.constants import Action, ManaColor, CARD_TO_PLAY
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from mtggympy.gameengine.cards.instances.basiclands import Wastes, WASTES_NAME
from mtggympy.gameengine.cards.instances.types import CardInstance
import mtggympy.gameengine.transition as Engine
from mtggympy.config import app_config
from mtggympy.helpers.dict_operations import dicts_equal_with_default
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
        Engine.declare_blockers_step(0, Action.ATTACK, game_state)
        #Assert
        assert game_state.upcoming_event == PlayerEvent.MAINPHASE_1_EMPTY_STACK
        assert game_state.player_states[1].current_life == app_config.STARTING_LIFE - 1


    def test_drawing_a_card(self):
        #Setup
        game_state: GameState = get_default_game_state()
        #Execute:
        Engine.execute_action(0, game_state, Engine.draw_card)
        Engine.check_state_based_actions(game_state)
        #Assert
        assert len(game_state.player_states[0].cards_in_hand) == len(get_default_game_state().player_states[0].cards_in_hand) + 1
        assert len(game_state.player_states[0].cards_in_library) == len(get_default_game_state().player_states[0].cards_in_library) - 1

    def test_decking(self):
        #Setup
        game_state: GameState = get_default_game_state()
        game_state.player_states[0].cards_in_library = []
        #Execute        
        Engine.execute_action(0, game_state, Engine.draw_card)
        Engine.check_state_based_actions(game_state)
        #Assert
        assert game_state.game_over == True
        assert 1 in game_state.winner_positions

    def test_mana_production(self):
        #Setup
        game_state: GameState = get_default_game_state()
        game_state.player_states[0].cards_in_play = [
            Wastes(),
            CardInstance(CreatureNames.ALPHA_MYR.value),
            Wastes()
        ]
        #Execute
        Engine.activate_lands(acting_seat=0, game_state=game_state)
        #Assert
        expected_mana_pool: dict[ManaColor, int]={
            ManaColor.COLORLESS: 2
        }
        assert game_state.floating_mana == expected_mana_pool
        for card in game_state.player_states[0].cards_in_play:
            if isinstance(card, Wastes):
                assert card.tapped 
    
    def test_card_playing_success(self):
        #Setup
        game_state: GameState = get_default_game_state()
        game_state.player_states[0].cards_in_play = []

        game_state.player_states[0].cards_in_hand = [
            CardInstance(CreatureNames.SLIVER_CONSTRUCT.value),
            Wastes()
        ]
        game_state.floating_mana = {
            ManaColor.COLORLESS: 4
        }
        game_state.active_player_index = 0
        game_state.upcoming_event = PlayerEvent.MAINPHASE_1_EMPTY_STACK

        #Execute
        Engine.play_card(0, game_state, WASTES_NAME)
        Engine.play_card(0, game_state, CreatureNames.SLIVER_CONSTRUCT.value)

        #Assert
        assert game_state.upcoming_event == PlayerEvent.MAINPHASE_1_EMPTY_STACK
        assert game_state.floating_mana == {ManaColor.COLORLESS: 1}
        assert next((True for card in game_state.player_states[0].cards_in_play if card.card_name == WASTES_NAME), False)
        assert next((True for card in game_state.player_states[0].cards_in_play if card.card_name == CreatureNames.SLIVER_CONSTRUCT.value), False)

    def test_first_main_phase_success(self):
        #Setup
        game_state: GameState = get_default_game_state()
        game_state.player_states[0].cards_in_play = []
        game_state.player_states[0].cards_in_hand = [
            CardInstance(CreatureNames.METALLIC_SLIVER.value),
            Wastes()
        ]
        game_state.active_player_index = 0
        game_state.upcoming_event = PlayerEvent.MAINPHASE_1_EMPTY_STACK

        # Mixed Execution
        Engine.step(0, Action.PLAY_CARD, game_state, decision_details={CARD_TO_PLAY: WASTES_NAME})
        assert next((True for card in game_state.player_states[0].cards_in_play if card.card_name == WASTES_NAME), False)

        Engine.step(0, Action.ACTIVATE_LANDS, game_state)
        assert dicts_equal_with_default(game_state.floating_mana, {ManaColor.COLORLESS: 1})

        Engine.step(0, Action.PLAY_CARD, game_state, decision_details={CARD_TO_PLAY: CreatureNames.METALLIC_SLIVER.value})
        assert dicts_equal_with_default(game_state.floating_mana, {ManaColor.COLORLESS: 0})
        assert next((True for card in game_state.player_states[0].cards_in_play if card.card_name == CreatureNames.METALLIC_SLIVER.value), False)

        Engine.step(0, Action.PASS, game_state)
        assert game_state.upcoming_event == PlayerEvent.DECLARE_ATTACKS

        #Assert


