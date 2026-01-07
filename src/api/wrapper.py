from __future__ import annotations

import numpy as np
import gymnasium as gym
import time
from threading import Thread
from gymnasium.spaces import Dict, Discrete, Box
from typing import Optional, TypeVar, Any

import app_config as app_const
import game.engine as MtgEngine
from game.decision_event import DecisionEvent, DECISION_EVENT_CATALOG
from game.state import GameState
from game.player import PlayerInfo
from server.multi_client_session import MultiClientSession as MtgSession
from server.player_connection import PlayerController
from agents.simple import Goldfish #, Monkey
from agents.api import ApiAgent
from agents.abstractions.base import AgentBase as Agent

from logging_config import ai_wrapper_log as logger


ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

type MtgObservation = dict[str, int | dict[str, int]]
type MtgAction = dict[str, int]
type MtgInfo = dict[str, Any]
type OpponentInfo = dict[str, int]



class MtgWrapper(gym.Env[MtgObservation, MtgAction]):

    def __init__(self) -> None:      
        # Set execution parameters
        self.agent: ApiAgent
        self.game_session: MtgSession
        self.session_thread: Thread
        self.internal_agents: list[Agent]

        # Define observation space
        self.observation_space = Dict({
            "upcoming_decision": Dict({
                "current_step": Discrete(2),
                "upcoming_decision_event": Discrete(1)
            }),
            "agent_is_active_player": Discrete(n=2),
            "agent_seat_position": Discrete(n=2),
            "agent_status": Dict({
                "hp": Box(low=0, high=app_const.STARTING_LIFE, dtype=np.int8),
                "card_in_hand": Box(low=0, high=app_const.DECK_SIZE, dtype=np.int8),
                "card_in_library": Box(low=0, high=app_const.DECK_SIZE, dtype=np.int8)
            }),
            "opponents_status": Dict({
                "hp": Box(low=0, high=app_const.STARTING_LIFE, dtype=np.int8),
                "card_in_hand": Box(low=0, high=app_const.DECK_SIZE, dtype=np.int8),
                "card_in_library": Box(low=0, high=app_const.DECK_SIZE, dtype=np.int8)
            })
        })

        # Define action space
        self.action_space = Dict({
           "decision_event": Discrete(2),
           "decision_index": Discrete(2) 
        })
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None) -> \
        tuple[MtgObservation, MtgInfo]:

        logger.info("Reseting environment ==> Setting up new session")
        # TODO: Enable Multiplayer
        # Employ singleton pattern on session
        # Implement seat negotiation
        # Implement external training management
        self.game_session = MtgSession() 

        # Set up extrenal agent
        self.agent = ApiAgent(self.game_session,"External", target_seat=0)
        agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)
        agent_thread.start()

        # Set up internal agent for the opponent
        self.internal_agents = []
        opponent = Goldfish(self.game_session, "Opp-Goldfish", target_seat=1) # Remember that this is the second seat due to 0 indexing
        self.internal_agents.append(opponent)
        opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)
        opponent_thread.start()

        self.session_thread = Thread(target=self.game_session.run_game, daemon=True)
        self.session_thread.start()
        
        return self.get_obs(), self._get_inf()

    def get_obs(self) -> MtgObservation:
        state: GameState = self.game_session.game_state
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        result: MtgObservation = {
            "upcoming_decision": {
                "current_step": state.steps_in_turn_completed,
                "upcoming_decision_event": self.get_index_of_decision(MtgEngine.get_upcoming_decision(state))
            },
            "agent_is_active_player": int(state.active_player_index == state.player_infos.index(agent_cont.player_info)),
            "agent_seat_position": agent_cont.position,
            "agent_status": self.get_player_info(agent_cont.position),
            #Assume two players for the momement
            "opponents_status": self.get_player_info((agent_cont.position + 1) % 2 )
        }
        return result
    
    def step(self, action: MtgAction) -> tuple[MtgObservation, int, bool, bool, MtgInfo]:
        with self.agent.api_lock:
            self.agent.api_action_input = DECISION_EVENT_CATALOG[action["decision_event"]].possible_actions[action["decision_index"]]
        assert self.agent.controller is not None
        while self.agent.controller.upcoming_decision is None:
            time.sleep(app_const.API_TICK_LENGTH)
        
        # Obs, Reward, terminated, truncated, info
        return self.get_obs(), 0, False, False, {}

    def _get_inf(self) -> dict[str, Any]:
        # TODO: Implement
        return {}
    
    def get_player_info(self, seat_position: int) -> OpponentInfo:
        player_info: PlayerInfo = self.game_session.game_state.player_infos[seat_position]
        return {
            "hp": player_info.current_life,
            "cards_in_hand": len(player_info.cards_in_hand),
            "cards_in_library": player_info.cards_in_library
        }
    
    def get_index_of_decision(self, decision: DecisionEvent) -> int:
        return DECISION_EVENT_CATALOG.index(decision)
    

