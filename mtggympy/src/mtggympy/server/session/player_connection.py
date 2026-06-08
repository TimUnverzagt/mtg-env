from __future__ import annotations

from mtggympy.gameengine.player import PlayerInfo
from mtggympy.gameengine.priority.event import EventData
from mtggympy.gameengine.state import GameState
from mtggympy.gameengine.constants import Action
from threading import Condition
from logging import Logger
from mtggympy.logging_config import create_logger
import mtggympy.app_config as app_config

from typing import Callable


class PlayerController:
    def __init__(self, player_info: PlayerInfo, position: int, name: str, initial_game_state: GameState):
        self.player_info: PlayerInfo = player_info
        self.player_info.name = name
        self.logger: Logger = create_logger(name, app_config.PLAYER_LOG_LEVEL)
        self.terminate: bool = False
        self.session_condition: Condition = Condition()
        self.upcoming_event: EventData | None = None
        self.game_state_before_action: GameState | None = initial_game_state
        self.game_state_after_action: GameState | None = None
        self.intended_next_decision: Action | None = None
        self.position: int = position

    def set_action_result(self, new_state: GameState) -> None:
        self.upcoming_event = None
        self.intended_next_decision = None
        self.game_state_before_action = None
        self.game_state_after_action = new_state

    def get_session_ready_predicate(self) -> Callable[[], bool]:
        return lambda: (self.upcoming_event is not None) and (self.game_state_before_action is not None)
    
    def get_intent_predicate(self, expected_to_be_set: bool) -> Callable[[], bool]:
        return lambda: (self.intended_next_decision is not None) == expected_to_be_set 
    
    def get_action_result_predicate(self, expected_to_be_set: bool) -> Callable[[], bool]:
        return lambda: (self.game_state_after_action is not None) == expected_to_be_set 
