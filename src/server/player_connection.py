from __future__ import annotations

from game_engine.player import Player
from game_engine.base import BaseEngine
from game_engine.decision_event import DecisionEvent
from threading import Lock
from logging import Logger


class PlayerController:
    def __init__(self, player: Player, logger: Logger, position: int):
        self.player: Player = player
        self.logger: Logger = logger
        self.terminate: bool = False
        self.lock: Lock = Lock()
        self.upcoming_decision: DecisionEvent | None = None
        self.intended_next_decision: str | None = None
        self.position: int = position

    
    def reset_decision_info(self) -> None:
        self.upcoming_decision = None
        self.intended_next_decision = None

class SessionSeat:
    def __init__(self, env: BaseEngine, controller: PlayerController) -> None:
        self.controller: PlayerController = controller
        controller.logger.info("Connecting agent to the session player {}".format(self.controller.player.name))
        self.env: BaseEngine = env
