from abc import ABC, abstractmethod
from server.session.multi_client_session import MultiClientSession as GameSession
from gameengine.priority.base import PriorityEvent
from server.session.player_connection import PlayerController
from helpers.predicate_extensions import build_either_predicate
from gameengine.enums import Action

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

            with cont.session_condition:
                cont.logger.debug("{}: Waiting for my turn to act. (Signaled by session setting upcoming_decision)".format(cont.player_info.name))
                cont.session_condition.wait_for(build_either_predicate(
                    cont.get_session_ready_predicate(),
                    lambda: self.session.shutting_down))
                if self.session.shutting_down:
                    continue
                assert cont.upcoming_decision is not None

                cont.logger.info("{}: Thinking on next event '{}'.".format(cont.player_info.name, cont.upcoming_decision.applicable_phase))
                cont.intended_next_decision = self.decide_on_action(cont.upcoming_decision)
                cont.upcoming_decision = None
                cont.logger.info("{}: Decided on action '{}'.".format(cont.player_info.name, cont.intended_next_decision))
                cont.session_condition.notify_all()

                cont.logger.debug("{}: Waiting for the session to consume my intent".format(cont.player_info.name))
                cont.session_condition.wait_for(cont.get_intent_predicate(expected_to_be_set=False))
                
                cont.logger.debug("{}: Waiting for response from game session.".format(cont.player_info.name))
                cont.session_condition.wait_for(cont.get_action_result_predicate(expected_to_be_set=True))
                cont.logger.debug("{}: Got response from game session.".format(cont.player_info.name))

        cont.logger.info("Stopping because session is shutting down")
        self.shutdown()


    @abstractmethod
    def decide_on_action(self, upcoming_action: PriorityEvent) -> Action:
        pass

    def shutdown(self) -> None:
        pass