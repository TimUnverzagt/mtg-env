from server.session.multi_client_session import MultiClientSession as GameSession
from gameengine.priority.base import PriorityEvent
from server.agents.abstractions.base import AgentBase

class ConsoleAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)

    def decide_on_action(self, upcoming_action: PriorityEvent) -> str:
        return self._get_input_for_event(upcoming_action)
    
    def _get_input_for_event(self, action_event: PriorityEvent) -> str:
        print ("Upcoming Event: {}".format(action_event.name))
        while True:
            intent: str = input("Please input one from the following actions: [{}]\nInput: ".format(
                action_event.possible_actions
            ))
            if intent in action_event.possible_actions:
                return intent
            print("Invalid input! Try again.")
    
    def shutdown(self) -> None:
        return