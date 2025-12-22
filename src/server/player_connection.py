from __future__ import annotations

from game.player import PlayerInfo
from game.decision_event import DecisionEvent
from game.state import GameState
from threading import Lock
from logging import Logger


class PlayerController:
    def __init__(self, player_info: PlayerInfo, logger: Logger, position: int):
        self.player_info: PlayerInfo = player_info
        self.logger: Logger = logger
        self.terminate: bool = False
        self.lock: Lock = Lock()
        self.upcoming_decision: DecisionEvent | None = None
        self.last_known_game_state: GameState | None = None
        self.intended_next_decision: str | None = None
        self.position: int = position

    
    def set_action_result(self, new_state: GameState) -> None:
        self.upcoming_decision = None
        self.intended_next_decision = None
        self.last_known_game_state = new_state

class SessionSeat:
    def __init__(self, controller: PlayerController) -> None:
        self.controller: PlayerController = controller
        controller.logger.info("Connecting agent to the session player {}".format(self.controller.player_info.name))
