from __future__ import annotations
from enum import Enum
import numpy as np


import gymnasium as gym
from threading import Thread
from gymnasium.spaces import Discrete, Tuple, MultiDiscrete, Space
from typing import Optional, TypeVar, Any, cast


#import game.engine as MtgEngine
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.gameengine.state.core import GameState
from mtggympy.server.session.multi_client import MultiClientSession as MtgSession
from mtggympy.server.session.observed_state import ObservedGameState
from mtggympy.server.session.player_controller import PlayerController
from mtggympy.server.agents.simple import Goldfish #, Monkey
from mtggympy.server.agents.external import ApiAgent
from mtggympy.server.agents.base import AgentBase as Agent
from mtggympy.api.gym.encoding import FlatMtgAction, FlatMtgObservation, MtgObservation, MtgInfo, MtgAction
import mtggympy.api.gym.encoding as encoding
from mtggympy.api.gym.translation import gym_action_to_player_decision, observed_state_to_obs
from mtggympy.helpers.predicate_extensions import build_either_predicate

from mtggympy.config.logging_config import api_log as logger

ACTION_REJECTED_INFO_KEY = "action_rejected"

GAME_WIN_REWARD: int = 10
GAME_LOSS_REWARD: int = -10
ACTION_REJECTION_REWARD: int = -1

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

class ObservationTarget(Enum):
    LAST = 0
    INITIAL = 1
    BEFORE_ACTION = 2
    AFTER_ACTION = 3

class StandaloneEnv(gym.Env[FlatMtgObservation, FlatMtgAction]):

    def __init__(self) -> None:      
        # Set execution parameters
        self.agent: ApiAgent
        self.game_session: MtgSession
        self.session_thread: Thread
        self.internal_agents: list[Agent]
        self.observation_limits: MtgObservation | None = None
        self.last_obs: MtgObservation | None = None
        self.steps_performed: int = 0

        card_space: MultiDiscrete = MultiDiscrete(
            [encoding.ASSUMED_NUMBER_OF_CARDS +1, 2, 2])
        

        # Define observation space
        self.nested_observation_space: Space[MtgObservation] = Tuple([
            Discrete(n=2), #agent_seat_position
            Discrete(n=encoding.ASSUMED_MAX_TURNS + 1), #turns played
            Discrete(n=3), #upcoming player event
            Discrete(n=2), #agent_is_active_player
            ################
            # SELF
            ################
            Tuple([
                Discrete(n=encoding.ASSUMED_INITIAL_HP + 1), #agent_hp
                Discrete(n=encoding.ASSUMED_INITIAL_DECK_SIZE + 1), #agent cards in deck
                Tuple([card_space]*encoding.ASSUMED_MAX_HAND_SIZE), #cards_in_hand
                Tuple([card_space]*encoding.ASSUMED_MAX_BATTLEFIELD_SIZE), #cards_in_play
            ]),
            ################
            # OPP
            ################
            Tuple([
                Discrete(n=encoding.ASSUMED_INITIAL_HP + 1), #opponent_hp
                Discrete(n=encoding.ASSUMED_INITIAL_DECK_SIZE + 1), #opponent in deck
                Discrete(n=encoding.ASSUMED_MAX_HAND_SIZE + 1), #opponent_in_hand 
                Tuple([card_space]*encoding.ASSUMED_MAX_BATTLEFIELD_SIZE), #cards_in_play
            ])
        ])
        #print(encoding.get_space_sizes(self.nested_observation_space))
        #print(sum(encoding.get_space_sizes(self.nested_observation_space)))
        #print(encoding.OBSERVATION_DIMS)
        #print(encoding.SELF_OBS_ENCODING_LIMIT[2].shape)
        #print(encoding.SELF_OBS_ENCODING_LIMIT[3].shape)
        assert sum(encoding.get_space_sizes(self.nested_observation_space)) == encoding.OBSERVATION_DIMS
        self.observation_space: Space[FlatMtgObservation] = encoding.flatten_tuple_of_discrete_spaces(self.nested_observation_space)

        # Define action space
        self.nested_action_space: Space[MtgAction]  =  Tuple([
            Discrete(n=encoding.ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS),  #decision_intent
            MultiDiscrete( #Maximal possible action argument: incidence of pairs of card positions during block
                nvec=np.full(shape=(encoding.ASSUMED_MAX_BATTLEFIELD_SIZE, encoding.ASSUMED_MAX_BATTLEFIELD_SIZE), fill_value=2)
            )
        ])
        self.action_space: Space[FlatMtgAction] = encoding.flatten_tuple_of_discrete_spaces(self.nested_action_space)

        print(encoding.get_space_sizes(self.nested_action_space))
        assert sum(encoding.get_space_sizes(self.nested_action_space)) == encoding.ACTION_DIMS
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None) -> \
        tuple[FlatMtgObservation, MtgInfo]:

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
        return self.get_obs(), self._get_inf(intent_was_rejected=False)

    def get_obs(self) -> FlatMtgObservation:
        logger.debug("Returning last obs: {}".format(self.last_obs))
        assert self.last_obs
        return encoding.flatten_observation(self.last_obs)
    
    def get_end_of_game_reward(self) -> int:
        state: GameState = self.game_session.game_state
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        if agent_cont.position in state.winner_positions:
            return GAME_WIN_REWARD
        else:
            return GAME_LOSS_REWARD

    
    def step(self, action: FlatMtgAction) -> tuple[FlatMtgObservation, int, bool, bool, MtgInfo]:
        logger.debug("Performing a step of the enironment")
        reward: int = 0
        terminated: bool = False
        truncated: bool = False
        info: MtgInfo = self._get_inf(intent_was_rejected=False)

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

        flat_action: Any = encoding.explode_flat_action(action)
        logger.info("Step {}: Got external intent {} into action intent".format(self.steps_performed + 1, flat_action[0]))
        intent: ActionIntent = gym_action_to_player_decision(prior_state.event, encoding.explode_flat_action(action))
        logger.info("Step {}: Got internal intent {} as translation for gymnasium action".format(self.steps_performed + 1,intent.action.name))
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
            if(self.agent.controller.obs_last_action_rejected):
                reward += ACTION_REJECTION_REWARD
                info = self._get_inf(intent_was_rejected=True)
                logger.warning("Step {}: Intent resulted in rejected action".format(self.steps_performed + 1))
                self.agent.controller.obs_last_action_rejected=False
            self.last_obs = observed_state_to_obs(posteriori_state, self.observation_limits)
            self.agent.api_posteriori_state = None
            self.agent.api_posteriori_state_processing_condition.notify_all()

        if self.agent.controller.terminate:
            logger.info("Step {}: Controller is terminating ==> Sending terminated".format(self.steps_performed + 1))
            reward = self.get_end_of_game_reward()
            terminated = True

        self.steps_performed += 1
        return self.get_obs(), reward, terminated, truncated, info

    def _get_inf(self, intent_was_rejected: bool) -> MtgInfo:
        infos: dict[str, Any] = {}
        infos[ACTION_REJECTED_INFO_KEY] = intent_was_rejected
        return infos

    
if __name__ == "__main__":
    env = StandaloneEnv()
    print("")
    print("-" * 50)
    print("-" * 10 + " Observation Space Info")
    print("-" * 50)
    print(cast(Tuple, env.nested_observation_space))
    print("Dimensions in nested space: {}".format(encoding.OBSERVATION_DIMS))    
    print(encoding.flatten_tuple_of_discrete_spaces(cast(Tuple, env.nested_observation_space)))
    obs_sample: MtgObservation = env.nested_observation_space.sample()
    print("Orignal Sample:")
    print(obs_sample)
    print("Flattened sample:")
    print(encoding.flatten_observation(obs_sample))

    print("")
    print("-" * 50)
    print("-" * 10 + " Action Space Info")
    print("-" * 50)
    print(cast(Tuple, env.nested_action_space))
    print("Dimensions in nested space: {}".format(encoding.ACTION_DIMS))
    print(encoding.flatten_tuple_of_discrete_spaces(cast(Tuple, env.nested_action_space)))
    action_sample: MtgAction = env.nested_action_space.sample()
    print("Orignal Sample:")
    print(action_sample)
    flattened_action_sample=encoding.flatten_action(action_sample)
    print("Flattened sample:")
    print(flattened_action_sample)
    print("Reinflated sample:")
    print(encoding.explode_flat_action(flattened_action_sample))