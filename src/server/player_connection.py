from __future__ import annotations

from environment.player import Player
from environment.base import BaseEnvironment
from environment.decision_event import DecisionEvent
from threading import Thread, Lock

import time
from logging import Logger


class PlayerController:
    def __init__(self, player: Player, logger: Logger):
        self.player: Player = player
        self.logger: Logger = logger
        self.terminate: bool = False
        self.lock: Lock = Lock()
        self.upcoming_decision: DecisionEvent | None = None
        self.intended_next_decision: str | None = None

    
    def reset_decision_info(self) -> None:
        self.upcoming_decision = None
        self.intended_next_decision = None

class SessionSeat:
    def __init__(self, env: BaseEnvironment, controller: PlayerController) -> None:
        self.controller: PlayerController = controller
        controller.logger.info("Connecting agent to the session player {}".format(self.controller.player.name))
        self.env: BaseEnvironment = env
        self.player_thread: Thread = Thread(target=self.run_player_thread, daemon=True, args=[self.controller])
        self.player_thread.start()

    def run_player_thread(self, controller: PlayerController) -> None:
        seconds_connected:int = 0
        while True:
            if not self.controller.player.is_alive():
                self.controller.logger.info("Player died by {}!".format(self.controller.player.death_description))
                self.controller.logger.info("Closing PlayerThread")
                return
            time.sleep(1)
            seconds_connected += 1
            controller.logger.debug("Player {} has been connected for {} seconds.".format(
                self.controller.player.name, seconds_connected))
