from abc import ABC, abstractmethod
from server.multi_client_session import MultiClientSession as GameSession
from game.decision_event import DecisionEvent
from server.player_connection import PlayerController

import time
from logging_config import main_log
import app_config as conf

class AgentBase(ABC):

    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        self.session: GameSession = session
        self.controller: PlayerController | None
        if target_seat is None:
            self.controller = session.connect(name)
        else:
            self.controller = session.connect_to_seat(target_seat, name)
        assert self.controller is not None

    def play_game(self) -> None:
        cont: PlayerController | None = self.controller
        if cont is None:
            main_log.error("Agent has no Connection to an active GameSession!")
            return
        last_timestamp: float = time.time()
        delta_t: float = 0.0
        while not self.session.shutting_down:
            delta_t = time.time() - last_timestamp
            last_timestamp = time.time()
            if (delta_t < conf.AGENT_TICK_LENGTH):
                time.sleep(max(conf.AGENT_TICK_LENGTH - delta_t, 0))

            if cont.upcoming_decision is None or cont.game_state_before_action is None:
                cont.logger.debug("{}: Waiting for my turn to act. (Signaled by session setting upcoming_decision)".format(cont.player_info.name))
                continue

            if cont.intended_next_decision is not None:
                cont.logger.debug("{}: Waiting for the session to accept my intent".format(cont.player_info.name))
                continue
            
            with cont.lock:
                cont.logger.info("{}: Thinking on next event '{}'.".format(cont.player_info.name, cont.upcoming_decision.name))
                cont.intended_next_decision = self.decide_on_action(cont.upcoming_decision)
                cont.logger.info("{}: Decided on action '{}'.".format(cont.player_info.name, cont.intended_next_decision))

            if cont.game_state_after_action is None:
                cont.logger.debug("{}: Waiting for response from game session.".format(cont.player_info.name))
                continue

        cont.logger.info("Stopping because session is shutting down")


    @abstractmethod
    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        pass