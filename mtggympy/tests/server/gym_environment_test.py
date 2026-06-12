from mtggympy.gameengine.state import GameState
from mtggympy.gameengine.priority.event import PlayerEvent

from mtggympy.server.session.player_connection import PlayerController
import mtggympy.server.translation as translation
from mtggympy.api.gym_environment import MtgEnv, MtgObservation

from mtggympy.app_config import DECK_SIZE, STARTING_LIFE

from tests.default_data import get_default_game_state

mainphase_index: int = translation.event_to_index(PlayerEvent.MAINPHASE_1_EMPTY_STACK)
combat_index: int = translation.event_to_index(PlayerEvent.DECLARE_ATTACKS)

class TestApi():


    def test_raw_observations(self):
        #Setup
        api_under_test: MtgEnv = MtgEnv()

        game_state: GameState = get_default_game_state()

        api_under_test.reset()
        agent_cont: PlayerController | None = api_under_test.agent.controller
        assert agent_cont is not None
        agent_cont.game_state_after_action = game_state
        game_state.active_player_index = 0
        agent_cont.position = 1

        #Execute
        obs: MtgObservation = api_under_test.get_obs()

        #Assert
        #print(obs)
        expected_obs: MtgObservation = (
            combat_index, #upcoming_decision
            int(False), #agent_is_active_player
            1, #agent_seat_position
            (STARTING_LIFE, 1, DECK_SIZE),
            (STARTING_LIFE, 1, DECK_SIZE)
        )
        assert obs == expected_obs


    def test_limited_observations(self):
        #Setup
        api_under_test: MtgEnv = MtgEnv()

        game_state: GameState = get_default_game_state()
        observation_limits: MtgObservation = (1, 1, 1, (2, 0, 4), (4, 0, 2))
        api_under_test.reset(options={"observation_limits": observation_limits})

        agent_cont: PlayerController | None = api_under_test.agent.controller
        assert agent_cont is not None
        agent_cont.game_state_after_action = game_state
        game_state.active_player_index = 0
        agent_cont.position = 1


        #Execute
        obs: MtgObservation = api_under_test.get_obs()

        #Assert
        #print(obs)
        expected_obs: MtgObservation = (
            combat_index, #upcoming_decision
            int(False), #agent_is_active_player
            1, #agent_seat_position
            (min(2, STARTING_LIFE), 0, min(4, DECK_SIZE)),
            (min(4, STARTING_LIFE), 0, min(2, DECK_SIZE))
        )

        assert obs == expected_obs    