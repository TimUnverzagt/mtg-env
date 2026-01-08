import unittest
from operator import attrgetter

from game.state import GameState
from game.player import PlayerInfo
from game.card import Card
from game.decision_event import DECISION_EVENT_CATALOG
import game.constants as GameConsts

from api.wrapper import MtgEnv, MtgObservation, game_state_to_obs

class TestAiWrapper(unittest.TestCase):

    def test_observations(self):
        #Setup
        wrapper_under_test: MtgEnv = MtgEnv()

        alice_info: PlayerInfo = PlayerInfo("Alice", 3, [Card(1)], 5, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 3, [Card(1), Card(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info]
        )

        wrapper_under_test.reset()

        #Execute
        obs: MtgObservation = game_state_to_obs(game_state, 0)

        #Assert
        #print(obs)
        combat_index: int = list(map(attrgetter("name"), DECISION_EVENT_CATALOG)).index(GameConsts.COMBAT)
        expected_obs: MtgObservation = {
            "upcoming_decision": {
                "current_step": 1,
                "upcoming_decision_event": combat_index
            },
            "agent_is_active_player": int(True),
            "agent_seat_position": 0,
            "agent_status": {
                "hp": 3,
                "cards_in_hand": 1,
                "cards_in_library": 5
            },
            "opponents_status": {
                "hp": 3,
                "cards_in_hand": 2,
                "cards_in_library": 10
            }
        }

        self.assertDictEqual(obs, expected_obs)

if __name__ == '__main__':
    unittest.main()