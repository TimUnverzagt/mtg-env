import unittest
from operator import attrgetter

from game.state import GameState
from game.player import PlayerInfo
from game.card import Card
from game.decision_event import DECISION_EVENT_CATALOG
import game.constants as GameConsts

from server.api import MtgEnv, MtgObservation

combat_index: int = list(map(attrgetter("name"), DECISION_EVENT_CATALOG)).index(GameConsts.COMBAT)
mainphase_index: int = list(map(attrgetter("name"), DECISION_EVENT_CATALOG)).index(GameConsts.MAINPHASE)

class TestApi(unittest.TestCase):


    def test_raw_observations(self):
        #Setup
        api_under_test: MtgEnv = MtgEnv()

        agent_info: PlayerInfo = PlayerInfo("External", 3, [Card(1)], 5, None)
        opp_info: PlayerInfo = PlayerInfo("Opp-Goldfish", 3, [Card(1), Card(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[opp_info, agent_info],
            upcoming_decision=DECISION_EVENT_CATALOG[1],
            winner_positions=[]
        )

        api_under_test.reset()
        api_under_test.game_session.game_state = game_state

        #Execute
        obs: MtgObservation = api_under_test.get_obs()

        #Assert
        #print(obs)
        expected_obs: MtgObservation = (
            combat_index, #upcoming_decision
            int(False), #agent_is_active_player
            1, #agent_seat_position
            (3, 1, 5),
            (3, 2, 10)
        )
        self.assertEqual(obs, expected_obs)


    def test_limited_observations(self):
        #Setup
        api_under_test: MtgEnv = MtgEnv()

        agent_info: PlayerInfo = PlayerInfo("External", 3, [Card(1)], 5, None)
        opp_info: PlayerInfo = PlayerInfo("Opp-Goldfish", 3, [Card(1), Card(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[opp_info, agent_info],
            upcoming_decision=DECISION_EVENT_CATALOG[1],
            winner_positions=[]
        )
        observation_limits: MtgObservation = (1, 1, 1, (2, 0, 4), (4, 0, 2))
        api_under_test.reset(options={"observation_limits": observation_limits})
        api_under_test.game_session.game_state = game_state

        #Execute
        obs: MtgObservation = api_under_test.get_obs()

        #Assert
        #print(obs)
        expected_obs: MtgObservation = (
            combat_index, #upcoming_decision
            int(False), #agent_is_active_player
            1, #agent_seat_position
            (2, 0, 4),
            (3, 0, 2)
        )

        self.assertEqual(obs, expected_obs)    
        

if __name__ == '__main__':
    unittest.main()