from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, Box
from typing import Optional, TypeVar, Any

import agents.constants as ag_const
import package.app_config as app_const
import game.constants as game_const
from package.game.engine import GameEngine as MtgEngine
from game.decision_event import DecisionEvent
from server.multi_client_session import MultiClientSession as MtgSession
from server.player_connection import PlayerController
from agents.simple import Goldfish #, Monkey
from agents.abstractions.base import AgentBase as Agent
from threading import Thread

from package.logging_config import ai_wrapper_log as logger


ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

type MtgObservation = dict[str, int | dict[str, int]]
type MtgAction = dict[str, int]
type MtgInfo = dict[str, Any]

class MtgEnv(gym.Env[MtgObservation, MtgAction]):

    def __init__(self) -> None:        
        # Set execution parameters
        self.agent: Agent
        self.opponent: Agent
        self.opponent_type: str
        self.game_session: MtgSession

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
           "possible_actions": Discrete(2) 
        })
    
    def reset(self, *, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None) -> \
        tuple[MtgObservation, MtgInfo]:

        play_solo: bool = True
        self.opponent_type: str = ag_const.NEUTRAL
        self.game_session= MtgSession() # TODO: Employ singleton pattern to enable Multiplayer

        assert play_solo is True # TODO: Multiplayer
        if(play_solo):
            # Set up agent
            agent = Goldfish(self.game_session, target_seat=0)
            agent_thread: Thread = Thread(target=agent.play_game, daemon=True)
            agent_thread.start()

            # Set up opponent for solo player
            opponent = Goldfish(self.game_session, target_seat=1) # Remember that this is the second seat due to 0 indexing
            opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)
            opponent_thread.start()
        else:
            # 1. Fail if Session is already full
            # 2. Place agent empty seat
            # 3. Set seat information based on placement
            logger.error("Multiplayer is not yet suppoorted. Programm is expected to crash soon!")
        return self._get_obs(), self._get_inf()

    def _get_obs(self) -> MtgObservation:
        engine: MtgEngine = self.game_session.env
        agent_cont: PlayerController | None = self.agent.controller
        assert agent_cont is not None
        op_cont: PlayerController | None = self.opponent.controller
        assert op_cont is not None 
        result: dict[str, int | dict[str, int]] = {
            "upcoming_decision": {
                "current_step": engine.game_state.steps_in_turn_completed,
                "upcoming_decision_event": self._get_index_of_decision(engine.get_upcoming_decision())
            },
            "agent_is_active_player": int(engine.game_state.active_player_index == engine.game_state.player_infos.index(agent_cont.player_info)),
            "agent_seat_position": agent_cont.position,
            "agent_status": {
                "hp": agent_cont.player_info.current_life,
                "card_in_hand": len(agent_cont.player_info.cards_in_hand),
                "card_in_library": agent_cont.player_info.cards_in_library
            },
            "opponents_status": {
                "hp": op_cont.player_info.current_life,
                "card_in_hand": len(op_cont.player_info.cards_in_hand),
                "card_in_library": op_cont.player_info.cards_in_library
            }
        }
        return result
    
    def _get_inf(self) -> dict[str, Any]:
        # TODO: Implement
        return {}
    
    def _get_index_of_decision(self, decision: DecisionEvent) -> int:
        return game_const.DECISION_EVENT_CATALOG.index(decision)
    

