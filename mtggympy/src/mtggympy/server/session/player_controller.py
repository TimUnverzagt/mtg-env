from __future__ import annotations

from mtggympy.config.defaults import PlayerState
from mtggympy.gameengine.state.event import ActionIntent
from threading import Condition
from logging import Logger
from mtggympy.config.logging_config import create_logger, PLAYER_LOG_LEVEL
from mtggympy.server.session.observed_state import ObservedGameState


class PlayerController:
    def __init__(self, player_info: PlayerState, position: int, name: str, initial_game_state: ObservedGameState):
        self.player_info: PlayerState = player_info
        self.player_info.name = name
        self.logger: Logger = create_logger(name, PLAYER_LOG_LEVEL)
        self.terminate: bool = False
        self.position: int = position
        self.initial_state: ObservedGameState = initial_game_state

        # Shared variables
        self.obs_before_action_condition: Condition = Condition()
        self.obs_before_action: ObservedGameState | None = None
        self.obs_after_action_condition: Condition = Condition()
        self.obs_after_action: ObservedGameState | None = None
        self.obs_last_action_rejected: bool = False
        self.intent_condition: Condition = Condition()
        self.intent: ActionIntent | None = None

    def set_action_priors(self, new_state: ObservedGameState):
        self.intent = None
        self.obs_before_action = new_state
        self.obs_after_action = None

    def set_action_result(self, new_state: ObservedGameState, action_rejected: bool) -> None:
        self.intent = None
        self.obs_after_action = new_state
        self.obs_last_action_rejected = action_rejected

    def propagate_termination(self) -> None:
        with self.obs_before_action_condition:
            self.obs_before_action_condition.notify_all()
        with self.intent_condition:
            self.intent_condition.notify_all()
        with self.obs_after_action_condition:
            self.obs_after_action_condition.notify_all()
