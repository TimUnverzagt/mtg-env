from server.multi_client_session import MultiClientSession as GameSession
from game.decision_event import DecisionEvent
from agents.abstractions.base import AgentBase

import app_config as conf
import time

class ApiAgent(AgentBase):
    def __init__(self, session: GameSession, target_seat: int | None =  None) -> None:
        super().__init__(session, target_seat)
        self.api_action_input: str | None = None 

    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        # We expect the PlayerController to be locked/handled while we do anything here
        while self.api_action_input is None:
            time.sleep(conf.API_TICK_LENGTH)
        return self.api_action_input
        
