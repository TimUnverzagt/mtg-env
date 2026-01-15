import unittest
from operator import attrgetter

from game.state import GameState
from game.player import PlayerInfo
from game.card import Card
from game.decision_event import DECISION_EVENT_CATALOG
import game.constants as GameConsts

from server.api import MtgEnv, MtgObservation, game_state_to_obs

class TestApi(unittest.TestCase):

    def test_observations(self):
        #Setup
        api_under_test: MtgEnv = MtgEnv()

        alice_info: PlayerInfo = PlayerInfo("Alice", 3, [Card(1)], 5, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 3, [Card(1), Card(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info],
            upcoming_decision=DECISION_EVENT_CATALOG[0],
            winner_positions=[]
        )

        api_under_test.reset()

        #Execute
        obs: MtgObservation = game_state_to_obs(game_state, 0)

        #Assert
        #print(obs)
        mainphase_index: int = list(map(attrgetter("name"), DECISION_EVENT_CATALOG)).index(GameConsts.MAINPHASE)
        expected_obs: MtgObservation = (
            mainphase_index, #upcoming_decision
            int(True), #agent_is_active_player
            0, #agent_seat_position
            (3, 1, 5),
            (3, 2, 10)
        )

        self.assertEqual(obs, expected_obs)

if __name__ == '__main__':
    unittest.main()