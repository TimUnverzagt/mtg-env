import unittest
from operator import attrgetter


from game.state import GameState
from game.player import PlayerInfo
from game.card import Card
from game.decision_event import DECISION_EVENT_CATALOG
import game.constants as GameConsts
from agents.simple import Goldfish, Monkey
from server.multi_client_session import MultiClientSession as GameSession
import helpers.type_guards as tg

from ai_wrapper.base import MtgWrapper, MtgObservation

class TestAiWrapper(unittest.TestCase):

    def test_observations(self):
        #Setup
        wrapper_under_test: MtgWrapper = MtgWrapper()

        alice_info: PlayerInfo = PlayerInfo("Alice", 3, [Card(1)], 5, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 3, [Card(1), Card(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info]
        )
        game_session: GameSession =  GameSession(game_state)
        agent1: Goldfish = Goldfish(game_session, 0)
        agent2: Monkey = Monkey(game_session, 1)

        wrapper_under_test.game_session = game_session
        wrapper_under_test.agent = agent1
        wrapper_under_test.opponent = agent2

        #Execute
        obs: MtgObservation = wrapper_under_test.get_obs()

        #Assert
        print(obs)
        assert tg.union_narrows_to_nested_map(obs["upcoming_decision"])
        self.assertEqual(obs["upcoming_decision"]["current_step"], 1)
        decision_index: int = list(map(attrgetter("name"), DECISION_EVENT_CATALOG)).index(GameConsts.COMBAT)
        self.assertEqual(obs["upcoming_decision"]["upcoming_decision_event"], decision_index)
        
        self.assertEqual(obs["agent_is_active_player"], 1)
        self.assertEqual(obs["agent_seat_position"], 0)

        assert tg.union_narrows_to_nested_map(obs["agent_status"])
        self.assertEqual(obs["agent_status"]["hp"], 3)
        self.assertEqual(obs["agent_status"]["cards_in_hand"], 1)
        self.assertEqual(obs["agent_status"]["cards_in_library"], 5)

        assert tg.union_narrows_to_nested_map(obs["opponents_status"])
        self.assertEqual(obs["opponents_status"]["hp"], 3)
        self.assertEqual(obs["opponents_status"]["cards_in_hand"], 2)
        self.assertEqual(obs["opponents_status"]["cards_in_library"], 10)
        



if __name__ == '__main__':
    unittest.main()