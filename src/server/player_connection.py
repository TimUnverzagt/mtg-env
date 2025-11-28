from __future__ import annotations

from environment.player import Player
from environment.base import BaseEnvironment
from environment.action_event import ActionEvent
from threading import Thread

import time

import logging
logger = logging.getLogger(__name__)


class PlayerController:
    def __init__(self, player: Player):
        self.player: Player = player
        self.terminate: bool = False
        self.upcoming_action: ActionEvent | None = None
        self.intended_next_action: str | None = None

class SessionSeat:
    def __init__(self, env: BaseEnvironment, controller: PlayerController) -> None:
        self.controller: PlayerController = controller
        logger.info("Connecting player {} to the session".format(self.controller.player.name))
        self.env: BaseEnvironment = env
        self.player_thread: Thread = Thread(target=self.run_player_thread, daemon=True, args=[self.controller])
        self.player_thread.start()

    def run_player_thread(self, controller: PlayerController) -> None:
        seconds_connected:int = 0
        while True:
            time.sleep(1)
            seconds_connected += 1
            logger.debug("Player {} has been connected for {} seconds.".format(
                self.controller.player.name, seconds_connected))
    
    def reset_controller(self) -> None:
        self.controller.upcoming_action = None
        self.controller.intended_next_action = None
