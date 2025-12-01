from abc import ABC, abstractmethod
from server.multi_client_session import MultiClientSession as GameSession
from environment.action_event import ActionEvent
from server.player_connection import PlayerController

import time
from logging_config import main_log

class AgentBase(ABC):

    def __init__(self, session: GameSession) -> None:
        self.session: GameSession = session
        self.controller: PlayerController | None = session.connect()

    def play_game(self) -> None:
        cont: PlayerController | None = self.controller
        if cont is None:
            main_log.error("Agent has no Connection to an active GameSession!")
            return
        while not self.session.env.game_over:
            time.sleep(1)
            if cont.upcoming_action is not None:
                cont.logger.info("{}: Thinking on next action.".format(cont.player.name))
                cont.intended_next_action = self.decide_on_action(cont.upcoming_action)
                cont.logger.info("{}: Decided on action '{}'.".format(cont.player.name, cont.intended_next_action))
            else:
                cont.logger.debug("{}: Waiting on game session.".format(cont.player.name))

    @abstractmethod
    def decide_on_action(self, upcoming_action: ActionEvent) -> str:
        pass