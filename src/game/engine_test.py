import unittest

from game.state import GameState
from game.player import PlayerInfo
from game.card import CardInstance
from game.decision_event import DECISION_EVENT_CATALOG
import game.constants as GameConsts
import game.engine as Engine


class TestGameEngine(unittest.TestCase):

    def test_attack_decision(self):
        #Setup 
        alice_info: PlayerInfo = PlayerInfo("Alice", 5, [CardInstance(1)], 10, None)
        bob_info: PlayerInfo = PlayerInfo("Bob", 5, [CardInstance(1)], 10, None)
        game_state: GameState = GameState(
            player_turns_completed=0,
            steps_in_turn_completed=1,
            active_player_index=0,
            game_over=False,
            player_infos=[alice_info, bob_info],
            upcoming_decision=DECISION_EVENT_CATALOG[0],
            winner_positions=[]
        )

        #Execute
        Engine.handle_combat_decision(0, GameConsts.COMBAT_ATTACK, game_state)

        #Assert
        self.assertEqual(bob_info.current_life, 4)

if __name__ == '__main__':
    unittest.main()
