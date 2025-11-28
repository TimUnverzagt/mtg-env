from server.multi_client_session import MultiClientSession as GameSession
from server.player_connection import PlayerController
from environment.action_event import ActionEvent
import environment.constants as EnvConsts

import time
import logging
logger = logging.getLogger(__name__)

class Goldfish:
    def __init__(self, session: GameSession) -> None:
        self.session: GameSession = session
        self.controller: PlayerController | None = session.connect()

    def play_game(self) -> None:
        cont: PlayerController | None = self.controller
        if cont is None:
            logger.error("Agent has no Connection to an active GameSession!")
            return
        while not self.session.env.game_over:
            time.sleep(1)
            if cont.upcoming_action is not None:
                logger.info("{}: Thinking on next action.".format(cont.player.name))
                cont.intended_next_action = self.decide_on_action(cont.upcoming_action)
            else:
                logger.info("{}: Waiting on game session.".format(cont.player.name))

    def decide_on_action(self, upcoming_action: ActionEvent) -> str:
        if upcoming_action.name == EnvConsts.COMBAT:
            return EnvConsts.COMBAT_PASS
        if upcoming_action.name == EnvConsts.MAINPHASE:
            return EnvConsts.MAINPHASE_PASS
        return "Confused noises"

        



