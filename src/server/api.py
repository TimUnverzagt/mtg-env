from __future__ import annotations

import gymnasium as gym
import time
from threading import Thread
from gymnasium.spaces import Discrete, Tuple, MultiDiscrete
from typing import Optional, TypeVar, Any

import app_config as app_const
#import game.engine as MtgEngine
from game.decision_event import DECISION_EVENT_CATALOG, DecisionEvent
from game.state import GameState
from game.player import PlayerInfo
from server.multi_client_session import MultiClientSession as MtgSession
from server.player_connection import PlayerController
from server.agents.simple import Goldfish #, Monkey
from server.agents.external import ApiAgent
from server.agents.abstractions.base import AgentBase as Agent

from logging_config import api_log as logger


ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

type MtgObservation = tuple[int, int, int, PlayerObs, PlayerObs]
type MtgAction = tuple[int]
type MtgInfo = dict[str, Any]
type PlayerObs = tuple[int, int, int]

    
def game_state_to_obs(state: GameState, agent_position: int) -> MtgObservation:
    player_info: PlayerInfo = state.player_infos[agent_position]
    #Assume two players for the momement
    opponent_info: PlayerInfo = state.player_infos[(agent_position + 1) % 2]
    result: MtgObservation = (
        DECISION_EVENT_CATALOG.index(state.upcoming_decision), #upcoming_decision
        int(state.active_player_index == agent_position), #agent_is_active_player
        agent_position, #agent_seat_position
        player_obs_from_info(player_info), #agent_status 
        player_obs_from_info(opponent_info), #opponents_status
    )
    return result

def action_to_decision_intent(upcoming_decision: DecisionEvent, action: MtgAction) -> str:
    logger.debug("Translating for decision [{}]".format(upcoming_decision))
    intent: str = upcoming_decision.possible_actions[action[0]]
    logger.debug("Translated external action {} into internal intent [{}]".format(action[0], intent))
    return intent

def player_obs_from_info(player_info: PlayerInfo) -> PlayerObs:
    #
    return (
        player_info.current_life, #hp
        len(player_info.cards_in_hand), #cards_in_hand
        player_info.cards_in_library #cards_in_library
    )

class MtgEnv(gym.Env[MtgObservation, MtgAction]):

    def __init__(self) -> None:      
        # Set execution parameters
        self.agent: ApiAgent
        self.game_session: MtgSession
        self.session_thread: Thread
        self.internal_agents: list[Agent]

        # Define observation space
        self.observation_space = Tuple([
            Discrete(n=2), #upcoming_decision
            Discrete(n=2), #agent_is_active_player
            Discrete(n=2), #agent_seat_position
            MultiDiscrete( #agent_status
                nvec= [app_const.STARTING_LIFE+1 , #hp 
                app_const.DECK_SIZE+1, #cards_in_hand 
                app_const.DECK_SIZE+1] #cards_in_library
            ),
            MultiDiscrete( #opponent_status
                nvec= [app_const.STARTING_LIFE+1 , #hp 
                app_const.DECK_SIZE+1, #cards_in_hand 
                app_const.DECK_SIZE+1] #cards_in_library
            ),
        ])

        # Define action space
        self.action_space =  Tuple([
            Discrete(n=2)  #decision_intent
        ])
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None) -> \
        tuple[MtgObservation, MtgInfo]:

        logger.info("Reseting environment ==> Setting up new session")
        # TODO: Enable Multiplayer
        # Employ singleton pattern on session
        # Implement seat negotiation
        # Implement external training management
        self.game_session = MtgSession() 

        # Set up extrenal agent
        self.agent = ApiAgent(self.game_session,"External", target_seat=1)
        agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)
        agent_thread.start()

        # Set up internal agent for the opponent
        self.internal_agents = []
        opponent = Goldfish(self.game_session, "Opp-Goldfish", target_seat=0) 
        self.internal_agents.append(opponent)
        opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)
        opponent_thread.start()

        self.session_thread = Thread(target=self.game_session.tick_session, daemon=True)
        self.session_thread.start()
        
        return self.get_obs(), self._get_inf()

    def get_obs(self) -> MtgObservation:
        state: GameState = self.game_session.game_state
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        return game_state_to_obs(state, agent_cont.position)
    
    def get_end_of_game_reward(self) -> int:
        state: GameState = self.game_session.game_state
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        reward: int = 10
        if agent_cont.position in state.winner_positions:
            return reward
        else:
            return reward * -1

    
    def step(self, action: MtgAction) -> tuple[MtgObservation, int, bool, bool, MtgInfo]:
        logger.debug("Performing a step of the enironment")
        reward: int = 0
        terminated: bool = False
        truncated: bool = False
        info: MtgInfo = {}



        assert self.agent.controller is not None        
        while self.agent.controller.upcoming_decision is None:
            # Catch game ending from other players game transitions
            if self.game_session.shutting_down:
                logger.info("Game ended between steps!")
                reward = self.get_end_of_game_reward()
                terminated = True
                return self.get_obs(), reward, terminated, truncated, info
            logger.debug("Waiting for upcoming decision to be set")
            
            time.sleep(app_const.API_TICK_LENGTH)

        upcoming_decision: DecisionEvent | None = None
        while upcoming_decision is None:
            upcoming_decision = self.agent.controller.upcoming_decision
        logger.debug("Current Upcoming Decision: {}".format(upcoming_decision.name))
        decision_intent: str = action_to_decision_intent(upcoming_decision, action)
            
        reward: int = 0
        terminated: bool = False
        truncated: bool = False
        info: MtgInfo = {}

        # Check for illegal actions
        #if not MtgEngine.is_legal_action(decision_intent, self.game_session.game_state):
        #    reward = -1
        #    return self.get_obs(), reward, terminated, truncated, info

        with self.agent.api_lock:
            logger.debug("Declaring decision intent from external action")
            self.agent.api_action_input = decision_intent

        while not self.game_session.shutting_down and self.agent.api_action_input is not None: # type: ignore (we wait for another thread to process the input)
            logger.debug("Waiting for intent to be processed")
            time.sleep(app_const.API_TICK_LENGTH)

        if self.game_session.shutting_down:
            logger.info("Game is over ==> Sending terminated")
            reward = self.get_end_of_game_reward()
            terminated = True
        
        return self.get_obs(), reward, terminated, truncated, info


    def _get_inf(self) -> dict[str, Any]:
        # TODO: Implement
        return {}
    

