from server.multi_client_session import MultiClientSession as GameSession
from game.decision_event import DecisionEvent
from agents.abstractions.base import AgentBase

import app_config as conf
import time
from threading import Lock

class ApiAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)
        self.api_action_input: str | None = None 
        self.api_lock: Lock = Lock()

    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        # We expect the PlayerController to be locked/handled while we do anything here
        while self.api_action_input is None:
            time.sleep(conf.API_TICK_LENGTH)
        with self.api_lock:
            intent: str = self.api_action_input
            self.api_action_input = None
            return intent
        
