from gameengine.state import GameState
from gameengine.player import PlayerInfo
from gameengine.gameobjects import CardInstance
from gameengine.priority.event import PlayerEvent
from gameengine.constants import Action
from gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
import gameengine.core as Engine
from collections import defaultdict


class TestGameEngine():

    def test_refusal_of_invalid_intent(self):
        #Setup
        alice_info: PlayerInfo = PlayerInfo("Alice", 5, [CardInstance(CreatureNames.ALPHA_MYR.value)], 10, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 5, [CardInstance(CreatureNames.ALPHA_MYR.value)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info],
            upcoming_event=PlayerEvent.DECLARE_ATTACKS,
            winner_positions=[],
            floating_mana=defaultdict(lambda: 0)
        )

        #Execute
        Engine.step(acting_seat=0, decision_intent=Action.PLAY_CARD, game_state=game_state)

        #Assert
        assert game_state.upcoming_event == PlayerEvent.DECLARE_ATTACKS

    def test_attack_decision(self):
        #Setup 
        alice_info: PlayerInfo = PlayerInfo("Alice", 5, [CardInstance(CreatureNames.ALPHA_MYR.value)], 10, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 5, [CardInstance(CreatureNames.ALPHA_MYR.value)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info],
            upcoming_event=PlayerEvent.DECLARE_ATTACKS,
            winner_positions=[],
            floating_mana=defaultdict(lambda: 0)
        )

        #Execute
        Engine.handle_combat_decision(0, Action.ATTACK, game_state)

        #Assert
        assert game_state.upcoming_event == PlayerEvent.MAIN_PHASE_EMPTY_STACK
        assert bob_info.current_life == 4
