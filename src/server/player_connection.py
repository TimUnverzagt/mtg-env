from __future__ import annotations

from game.player import PlayerInfo
from game.decision_event import DecisionEvent
from game.state import GameState
from threading import Lock
from logging import Logger
from logging_config import create_logger
import app_config


class PlayerController:
    def __init__(self, player_info: PlayerInfo, position: int, name: str, initial_game_state: GameState):
        self.player_info: PlayerInfo = player_info
        self.player_info.name = name
        self.logger: Logger = create_logger(name, app_config.PLAYER_LOG_LEVEL)
        self.terminate: bool = False
        self.lock: Lock = Lock()
        self.upcoming_decision: DecisionEvent | None = None
        self.game_state_before_action: GameState | None = initial_game_state
        self.game_state_after_action: GameState | None = None
        self.intended_next_decision: str | None = None
        self.position: int = position

    def set_action_result(self, new_state: GameState) -> None:
        self.upcoming_decision = None
        self.intended_next_decision = None
        self.game_state_before_action = None
        self.game_state_after_action = new_state
