from __future__ import annotations

from environment.player import Player
from environment.base import BaseEnvironment
from threading import Thread

import time

import logging
logger = logging.getLogger(__name__)


class PlayerController:
    def __init__(self):
        self.terminate: bool = False

class PlayerSocket:
    def __init__(self, player_name: str, env: BaseEnvironment, controller: PlayerController) -> None:
        self.player: Player = Player(player_name)
        self.env: BaseEnvironment = env
        self.player_thread: Thread = Thread(target=self.run_player_thread, args=[controller])

    def run_player_thread(self) -> None:
        seconds_connected:int = 0
        while True:
            time.sleep(1)
            seconds_connected += 1
            logger.info("Player {} has been connected for {} seconds.".format(
                self.player.name, seconds_connected))
