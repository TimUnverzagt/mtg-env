from __future__ import annotations
from enum import Enum

import gymnasium as gym
from threading import Thread
from gymnasium.spaces import Discrete, Tuple, MultiDiscrete
from typing import Optional, TypeVar, Any, cast

import mtggympy.config.app_config as app_const
from mtggympy.config.decks import DECK_SIZE
#import game.engine as MtgEngine
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.gameengine.state.core import GameState
from mtggympy.server.session.multi_client import MultiClientSession as MtgSession
from mtggympy.server.session.observed_state import ObservedGameState
from mtggympy.server.session.player_controller import PlayerController
from mtggympy.server.agents.simple import Goldfish #, Monkey
from mtggympy.server.agents.external import ApiAgent
from mtggympy.server.agents.base import AgentBase as Agent
from mtggympy.api.gym.types import MtgObservation, MtgInfo, MtgAction
from mtggympy.api.gym.translation import gym_action_to_player_decision, observed_state_to_obs
from mtggympy.helpers.predicate_extensions import build_either_predicate

from mtggympy.config.logging_config import api_log as logger


ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

class ObservationTarget(Enum):
    LAST = 0
    INITIAL = 1
    BEFORE_ACTION = 2
    AFTER_ACTION = 3

class StandaloneEnv(gym.Env[MtgObservation, MtgAction]):

    def __init__(self) -> None:      
        # Set execution parameters
        self.agent: ApiAgent
        self.game_session: MtgSession
        self.session_thread: Thread
        self.internal_agents: list[Agent]
        self.observation_limits: MtgObservation | None = None
        self.last_obs: MtgObservation | None = None
        self.steps_performed: int = 0

        # Define observation space
        self.observation_space = Tuple([
            Discrete(n=2), #upcoming_decision
            Discrete(n=2), #agent_is_active_player
            Discrete(n=2), #agent_seat_position
            MultiDiscrete( #agent_status
                nvec= [app_const.STARTING_LIFE+1 , #hp 
                DECK_SIZE+1, #cards_in_hand 
                DECK_SIZE+1] #cards_in_library
            ),
            MultiDiscrete( #opponent_status
                nvec= [app_const.STARTING_LIFE+1 , #hp 
                DECK_SIZE+1, #cards_in_hand 
                DECK_SIZE+1] #cards_in_library
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
        self.steps_performed = 0

        external_seat_pos = 1
        interal_seat_pos = 0
        # Set up external agent
        self.agent = ApiAgent(self.game_session,"External", target_seat=external_seat_pos)
        agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)


        # Set up internal agent for the opponent
        self.internal_agents = []
        opponent = Goldfish(self.game_session, "Opp-Goldfish", target_seat=interal_seat_pos) 
        self.internal_agents.append(opponent)
        opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)

        self.session_thread = Thread(target=self.game_session.tick_session, daemon=True)
        self.session_thread.start()
        agent_thread.start()
        opponent_thread.start()
        
        self.last_obs = observed_state_to_obs(self.agent.initial_state, self.observation_limits)
        return self.get_obs(), self._get_inf()

    def get_obs(self) -> MtgObservation:
        logger.debug("Returning last obs: {}".format(self.last_obs))
        assert self.last_obs
        return self.last_obs
    
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

        with self.agent.api_prior_state_processing_condition:
            logger.debug("Step {}: Waiting for prior state to be set".format(self.steps_performed + 1))
            self.agent.api_prior_state_processing_condition.wait_for(build_either_predicate(   
                lambda: self.agent.controller.terminate,
                lambda: self.agent.api_prior_state is not None  
            ))       
            if self.agent.controller.terminate:
                logger.info("Step {}: Game ended between steps! ==> Sending terminated".format(self.steps_performed + 1))
                terminated = True
                return (self.get_obs(),
                    self.get_end_of_game_reward(),
                    terminated, truncated, info)
            assert self.agent.api_prior_state
            prior_state: ObservedGameState = self.agent.api_prior_state
            self.last_obs = observed_state_to_obs(prior_state, self.observation_limits)
            logger.debug("Current Upcoming Event: {}".format(prior_state.event))
            self.agent.api_prior_state = None
            self.agent.api_prior_state_processing_condition.notify_all()

        logger.debug("Step {}: Translating gymnasium action {} into action intent".format(self.steps_performed + 1, action))
        intent: ActionIntent = gym_action_to_player_decision(prior_state.event, action)
        logger.info("Step {}: Got action {} as translation for gymnasium action".format(self.steps_performed + 1,intent.action.name))
        logger.debug("Step {}: Extracted the following params from gymnasium action: {}".format(self.steps_performed + 1, intent.parameters))

        with self.agent.api_intent_condition:
            logger.debug("Step {}: Declaring decision intent from external action".format(self.steps_performed + 1))
            self.agent.api_intent = intent
            self.agent.api_intent_condition.notify_all()
     

        with self.agent.api_posteriori_state_processing_condition:
            logger.debug("Step {}: waiting for response from agent".format(self.steps_performed + 1))
            self.agent.api_posteriori_state_processing_condition.wait_for(lambda: self.agent.api_posteriori_state is not None)
            assert self.agent.api_posteriori_state
            logger.debug("Step {}: Received processing confirmation via update of game state in controller".format(self.steps_performed + 1))
            posteriori_state = self.agent.api_posteriori_state
            self.last_obs = observed_state_to_obs(posteriori_state, self.observation_limits)
            self.agent.api_posteriori_state = None
            self.agent.api_posteriori_state_processing_condition.notify_all()

        if self.agent.controller.terminate:
            logger.info("Step {}: Controller is terminating ==> Sending terminated".format(self.steps_performed + 1))
            reward = self.get_end_of_game_reward()
            terminated = True

        self.steps_performed += 1
        return self.last_obs, reward, terminated, truncated, info

    def _get_inf(self) -> dict[str, Any]:
        # TODO: Implement
        return {}
    