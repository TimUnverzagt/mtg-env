from server.session.multi_client_session import MultiClientSession as GameSession
from gameengine.priority.base import PriorityEvent
from server.agents.abstractions.base import AgentBase
from threading import Condition
from typing import Callable
from helpers.predicate_extensions import build_either_predicate

from server.session.player_connection import PlayerController

class ApiAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)
        self.decision: PriorityEvent | None = None
        self.api_action_input: str | None = None 
        self.api_condition: Condition = Condition()

    def decide_on_action(self, upcoming_action: PriorityEvent) -> str:
        cont: PlayerController | None = self.controller
        assert cont is not None
        with self.api_condition:
            cont.logger.debug("Serving decision {} for api".format(upcoming_action))
            self.decision = upcoming_action
            self.api_condition.notify()
        
        with self.api_condition:
            cont.logger.debug("Waiting for consumption of decision and declaration of intent from api")
            self.api_condition.wait_for(build_either_predicate(
                lambda: self.decision is None,
                self.get_intent_declared_predicate(expected_to_be_set=True)))
            assert self.api_action_input is not None
            intent: str = self.api_action_input
            self.api_action_input = None
            cont.logger.debug("Declaration of intent received and consumed")
        
        return intent
    
    def shutdown(self) -> None:
        cont: PlayerController | None = self.controller
        assert cont is not None
        cont.logger.info("Shutting down agent!")
        with self.api_condition:
            self.api_condition.notify()
        
    
    def get_intent_declared_predicate(self, expected_to_be_set: bool) -> Callable[[], bool]:
        return lambda: (self.api_action_input is not None) == expected_to_be_set
        
