from logging import Logger
from typing import Callable

from mtggympy.server.session.multi_client import MultiClientSession as GameSession
from mtggympy.gameengine.state.event import ActionData, ActionIntent, PlayerEvent
from mtggympy.server.agents.abstractions.base import AgentBase
import mtggympy.gameengine.parsing as engine_parsing
from mtggympy.server.session.observed_state import ObservedGameState

class ConsoleAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None, wait_for_state_reading: bool = False) -> None:
        super().__init__(session, name, target_seat, wait_for_state_reading)

    def decide_on_action(self, state: ObservedGameState, logger: Logger) -> ActionIntent:
        return self._get_input_for_event(state.event)
    
    def _get_input_for_event(self, event: PlayerEvent) -> ActionIntent:
        print ("Upcoming Event: {}".format(event.name))
        while True:
            get_action_name: Callable[[ActionData], str] = lambda action: action.name
            action_names: list[str] = list(map(get_action_name, event.value.possible_actions))
            name_input: str = input("Please input one from the following actions: {}\nInput: ".format(
                action_names
            ))
            if name_input not in action_names:
                print("Invalid input! Try again.")
                continue
            intent: ActionIntent =  ActionIntent(ActionData[name_input], None)
            if intent.action.value.dimensionality <= 0:
                return intent
            argument_input: str = input(self._get_action_param_prompt(intent.action))
            intent.parameters = engine_parsing.collection_to_numpy(self._parse_action_input(intent.action, argument_input))
            return intent
            

    
    def _get_action_param_prompt(self, action: ActionData) -> str:
        prompt: str = "Input arguments in the following syntax --- {}\n"
        argument_coordinates: list[str] = []
        for n in range(0,action.value.dimensionality):
            argument_coordinates.append("int{}".format(n))
        argument_tuple_rep: str = ",".join(argument_coordinates)
        if not action.value.expects_collection:
            return prompt.format(argument_tuple_rep)
        argument_list_rep = "{};{};...".format(argument_tuple_rep, argument_tuple_rep)
        return prompt.format(argument_list_rep)
    
    def _parse_action_input(self, action: ActionData, input:str) -> list[list[int]]:
        seperated_arguments: list[str] = input.split(";")
        parsed_input: list[list[int]] = []
        for argument in seperated_arguments:
            parsed_input.append(list(map(int, argument.split(","))))

        return parsed_input
    
    def shutdown(self) -> None:
        return