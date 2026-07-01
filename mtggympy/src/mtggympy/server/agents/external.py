from logging import Logger

from mtggympy.server.session.multi_client import MultiClientSession as GameSession
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.server.agents.base import AgentBase
from threading import Condition

from mtggympy.server.session.observed_state import ObservedGameState
from mtggympy.server.session.player_controller import PlayerController

class ApiAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None, wait_for_state_reading: bool = False) -> None:
        super().__init__(session, name, target_seat, wait_for_state_reading)

        # Shared Variables 
        self.api_intent_condition: Condition = Condition()
        self.api_intent: ActionIntent | None = None 
        self.api_prior_state: ObservedGameState | None = None
        self.api_prior_state_processing_condition: Condition = Condition()
        self.api_posteriori_state: ObservedGameState | None = None
        self.api_posteriori_state_processing_condition: Condition = Condition()

    def decide_on_action(self, state: ObservedGameState, logger: Logger) -> ActionIntent:
        with self.api_intent_condition:
            self.api_intent = None
            logger.debug("Serving decision {} for api".format(state.event))
            self.api_intent_condition.notify()

            logger.debug("Waiting declaration of intent from api")
            self.api_intent_condition.wait_for(lambda: self.api_intent is not None)
            assert self.api_intent
            logger.debug("Declaration of intent received and consumed")       
            return self.api_intent
    
    def process_prior_state(self, state: ObservedGameState, logger: Logger) -> None:
        with self.api_prior_state_processing_condition:
            self.api_prior_state = state
            logger.debug("Set prior state and waiting for processing")
            self.api_prior_state_processing_condition.notify_all()
            self.api_prior_state_processing_condition.wait_for(lambda: self.api_prior_state is None)

    def process_posteriori_state(self, state: ObservedGameState, logger: Logger) -> None:
        with self.api_posteriori_state_processing_condition:
            self.api_posteriori_state = state
            logger.debug("Set posteriori state and waiting for processing")
            self.api_posteriori_state_processing_condition.notify_all()
            self.api_posteriori_state_processing_condition.wait_for(lambda: self.api_posteriori_state is None)
    
    def shutdown(self) -> None:
        cont: PlayerController | None = self.controller
        assert cont is not None
        cont.logger.info("Shutting down agent!")
        with self.api_prior_state_processing_condition:
            self.api_prior_state_processing_condition.notify_all()
        with self.api_intent_condition:
            self.api_intent_condition.notify()
        with self.api_posteriori_state_processing_condition:
            self.api_posteriori_state_processing_condition.notify_all()
        
