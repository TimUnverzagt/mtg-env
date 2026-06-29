from __future__ import annotations

from mtggympy.config.defaults import PlayerState
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.gameengine.state.core import GameState
from threading import Condition
from logging import Logger
from mtggympy.config.logging_config import create_logger
import mtggympy.config.app_config as app_config
from mtggympy.server.session.observed_state import ObservedGameState


class PlayerController:
    def __init__(self, player_info: PlayerState, position: int, name: str, initial_game_state: GameState):
        self.player_info: PlayerState = player_info
        self.player_info.name = name
        self.logger: Logger = create_logger(name, app_config.PLAYER_LOG_LEVEL)
        self.terminate: bool = False
        self.position: int = position

        # Shared variables
        self.obs_before_action_condition: Condition = Condition()
        self.obs_before_action: ObservedGameState | None = None
        self.obs_after_action_condition: Condition = Condition()
        self.obs_after_action: ObservedGameState | None = None
        self.intent_condition: Condition = Condition()
        self.intent: ActionIntent | None = None

    def set_action_priors(self, new_state: ObservedGameState):
        self.intent = None
        self.obs_before_action = new_state
        self.obs_after_action = None

    def set_action_result(self, new_state: ObservedGameState) -> None:
        self.intent = None
        self.obs_after_action = new_state
