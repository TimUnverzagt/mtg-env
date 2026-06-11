from mtggympy.server.session.multi_client_session import MultiClientSession as GameSession
from mtggympy.gameengine.priority.event import EventData
from mtggympy.gameengine.constants import Action
from mtggympy.server.agents.abstractions.base import AgentBase
from typing import Callable

class ConsoleAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None, wait_for_state_reading: bool = False) -> None:
        super().__init__(session, name, target_seat, wait_for_state_reading)

    def decide_on_action(self, upcoming_action: EventData) -> Action:
        return self._get_input_for_event(upcoming_action)
    
    def _get_input_for_event(self, action_event: EventData) -> Action:
        print ("Upcoming Event: {}".format(action_event.applicable_phase))
        while True:
            get_action_name: Callable[[Action], str] = lambda action: action.name
            action_names: list[str] = list(map(get_action_name, action_event.possible_actions))
            intent: str = input("Please input one from the following actions: [{}]\nInput: ".format(
                action_names
            ))
            if intent in action_names:
                return Action[intent]
            print("Invalid input! Try again.")
    
    def shutdown(self) -> None:
        return