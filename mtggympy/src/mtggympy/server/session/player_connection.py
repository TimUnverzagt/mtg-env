from __future__ import annotations

from mtggympy.gameengine.player import PlayerState
from mtggympy.gameengine.priority.event import ActionIntent, PlayerEvent
from mtggympy.gameengine.state import GameState
from threading import Condition
from logging import Logger
from mtggympy.logging_config import create_logger
import mtggympy.app_config as app_config

from typing import Callable

from mtggympy.server.obfuscation import observe_game_state
from mtggympy.server.session.observed_state import ObservedGameState


class PlayerController:
    def __init__(self, player_info: PlayerState, position: int, name: str, initial_game_state: GameState):
        self.player_info: PlayerState = player_info
        self.player_info.name = name
        self.logger: Logger = create_logger(name, app_config.PLAYER_LOG_LEVEL)
        self.terminate: bool = False
        self.session_condition: Condition = Condition()
        self.state_reading_condition: Condition = Condition()
        self.last_state_successfully_read: bool = False
        self.upcoming_event: PlayerEvent | None = None
        self.position: int = position
        self.obs_before_action: ObservedGameState | None = observe_game_state(initial_game_state, position)
        self.obs_after_action: ObservedGameState | None = None
        self.intended_next_decision: ActionIntent | None = None
        self.needs_processing_time: bool = False
        self.wait_for_state_reading: bool = False

    def set_action_priors(self, new_state: ObservedGameState, upcoming_event: PlayerEvent):
        self.upcoming_event = upcoming_event
        self.intended_next_decision = None
        self.obs_before_action = new_state
        self.obs_after_action = None
        self.last_state_successfully_read = False
        if self.wait_for_state_reading:
            self.needs_processing_time = True

    def set_action_result(self, new_state: ObservedGameState) -> None:
        self.upcoming_event = None
        self.intended_next_decision = None
        self.obs_before_action = None
        self.obs_after_action = new_state
        self.last_state_successfully_read = False
        if self.wait_for_state_reading:
            self.needs_processing_time = True

    def get_ready_for_session_consumption_predicate(self) -> Callable[[], bool]:
        return lambda: (self.upcoming_event is not None) and (self.obs_before_action is not None)
    
    def get_intent_predicate(self, expected_to_be_set: bool) -> Callable[[], bool]:
        return lambda: (self.intended_next_decision is not None) == expected_to_be_set 
    
    def get_action_result_predicate(self, expected_to_be_set: bool) -> Callable[[], bool]:
        return lambda: (self.obs_after_action is not None) == expected_to_be_set 
    
    def get_last_state_read_predicate(self, expected: bool) -> Callable[[], bool]:
        return lambda: self.last_state_successfully_read == expected
    
    def get_ready_for_next_loop_predicate(self) -> Callable[[], bool]:
        if(self.wait_for_state_reading):
            return lambda: not self.needs_processing_time
        else:
            return self.get_action_result_predicate(True)
