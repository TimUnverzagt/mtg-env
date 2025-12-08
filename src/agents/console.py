from server.multi_client_session import MultiClientSession as GameSession
from game_engine.decision_event import DecisionEvent
from agents.abstractions.base import AgentBase

class ConsoleAgent(AgentBase):
    def __init__(self, session: GameSession) -> None:
        super().__init__(session)

    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        return self._get_input_for_event(upcoming_action)
    
    def _get_input_for_event(self, action_event: DecisionEvent) -> str:
        print ("Upcoming Event: {}".format(action_event.name))
        while True:
            intent: str = input("Please input one from the following actions: [{}]\nInput: ".format(
                action_event.possible_actions
            ))
            if intent in action_event.possible_actions:
                return intent
            print("Invalid input! Try again.")