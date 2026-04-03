from __future__ import annotations

import gymnasium as gym
from threading import Thread
from gymnasium.spaces import Discrete, Tuple, MultiDiscrete
from typing import Optional, TypeVar, Any, cast

import app_config as app_const
#import game.engine as MtgEngine
from gameengine.state import GameState
from gameengine.constants import Action
from server.session.multi_client_session import MultiClientSession as MtgSession
from server.session.player_connection import PlayerController
from server.agents.simple import Goldfish #, Monkey
from server.agents.external import ApiAgent
from server.agents.abstractions.base import AgentBase as Agent
from server.api.gym_types import MtgObservation, MtgInfo, MtgAction
from server.translation import gym_action_to_priority_decision, game_state_to_obs
from helpers.tree_map import tree_map
from helpers.predicate_extensions import build_either_predicate

from logging_config import api_log as logger


ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

class MtgEnv(gym.Env[MtgObservation, MtgAction]):

    def __init__(self) -> None:      
        # Set execution parameters
        self.agent: ApiAgent
        self.game_session: MtgSession
        self.session_thread: Thread
        self.internal_agents: list[Agent]
        self.observation_limits: MtgObservation | None = None

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

        if options is not None and "observation_limits" in options:
            self.observation_limits = cast(MtgObservation, options["observation_limits"])

        logger.info("Reseting environment ==> Setting up new session")
        # TODO: Enable Multiplayer
        # Employ singleton pattern on session
        # Implement seat negotiation
        # Implement external training management
        self.game_session = MtgSession() 

        # Set up extrenal agent
        self.agent = ApiAgent(self.game_session,"External", target_seat=1)
        agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)


        # Set up internal agent for the opponent
        self.internal_agents = []
        opponent = Goldfish(self.game_session, "Opp-Goldfish", target_seat=0) 
        self.internal_agents.append(opponent)
        opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)

        self.session_thread = Thread(target=self.game_session.tick_session, daemon=True)
        self.session_thread.start()
        agent_thread.start()
        opponent_thread.start()
        
        assert self.agent.controller is not None
        self.agent.controller.game_state_after_action = self.agent.controller.game_state_before_action
        return self.get_obs(), self._get_inf()

    def get_obs(self) -> MtgObservation:
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        assert agent_cont.game_state_after_action is not None
        logger.debug("Constructing obs from following state {}".format(agent_cont.game_state_after_action))
        obs: MtgObservation = game_state_to_obs(agent_cont.game_state_after_action, agent_cont.position)
        if self.observation_limits is not None:
            obs = cast(MtgObservation, tree_map(min, obs, self.observation_limits))
        return obs
    
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
     
        with self.agent.api_condition:
            logger.debug("Waiting for upcoming decision to be set")
            self.agent.api_condition.wait_for(build_either_predicate(   
                lambda: self.agent.decision is not None,
                lambda: self.game_session.shutting_down,   
            ))       
            if self.game_session.shutting_down:
                logger.info("Game ended between steps!")
                reward = self.get_end_of_game_reward()
                terminated = True
                return self.get_obs(), reward, terminated, truncated, info
            
            assert self.agent.decision is not None
            logger.debug("Current Upcoming Decision: {}".format(self.agent.decision.applicable_phase))
            decision_intent: Action = gym_action_to_priority_decision(self.agent.decision, action)
            self.agent.decision = None
            self.agent.api_condition.notify()

            
        reward: int = 0
        terminated: bool = False
        truncated: bool = False
        info: MtgInfo = {}

        # Check for illegal actions
        #if not MtgEngine.is_legal_action(decision_intent, self.game_session.game_state):
        #    reward = -1
        #    return self.get_obs(), reward, terminated, truncated, info

        assert self.agent.controller is not None  
        # TODO: Uncouple Api from controller. Doesn't need to know about the agent-session communication  
        with self.agent.api_condition:
            logger.debug("Ensuring no intent is currently set")
            self.agent.api_condition.wait_for(self.agent.get_intent_declared_predicate(expected_to_be_set=False))
            logger.debug("Declaring decision intent from external action")
            # TODO: Translate external action to well typed decision intent
            self.agent.api_action_input = decision_intent
            logger.debug("Waiting for intent to be processed")
            self.agent.api_condition.wait_for(build_either_predicate(
                lambda: self.game_session.shutting_down,
                self.agent.controller.get_action_result_predicate(expected_to_be_set=True)
            ))
            logger.debug("Received processing confirmation via update of game state in controller")
            obs: MtgObservation = self.get_obs()
            self.agent.controller.game_state_after_action = None
            logger.debug("Consumed new game state information")


        if self.game_session.shutting_down:
            logger.info("Game is over ==> Sending terminated")
            reward = self.get_end_of_game_reward()
            terminated = True

        return obs, reward, terminated, truncated, info

    def _get_inf(self) -> dict[str, Any]:
        # TODO: Implement
        return {}
    