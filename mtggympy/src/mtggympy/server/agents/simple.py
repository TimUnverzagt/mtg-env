from logging import Logger

from mtggympy.server.session.multi_client import MultiClientSession as GameSession
from mtggympy.gameengine.state.event import ActionData, ActionIntent, EventData
#import environment.constants as EnvConsts
from mtggympy.server.agents.abstractions.base import AgentBase

from mtggympy.logging_config import main_log
import random
import sys
import numpy as np

from mtggympy.server.session.observed_state import ObservedGameState

class Goldfish(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)

    def decide_on_action(self, state: ObservedGameState, logger: Logger) -> ActionIntent:
        event_data: EventData = state.event.value
        neutral_index: int = event_data.neutral_action_index
        return ActionIntent(event_data.possible_actions[neutral_index], None)
    
class Monkey(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)
        seed: int = random.randrange(sys.maxsize)  
        self.random_generator = random.Random(seed)
        main_log.info("Random seed for monkey: {}".format(seed))

    def decide_on_action(self,  state: ObservedGameState, logger: Logger) -> ActionIntent:
        event_data: EventData = state.event.value
        random_index: int = self.random_generator.randint(0, len(event_data.possible_actions) - 1)
        random_action: ActionData = event_data.possible_actions[random_index]
        arguments: np.ndarray | None = None
        if random_action.value.dimensionality >= 1:
            arguments = np.random.randint(3, size=(1,random_action.value.dimensionality), dtype=int)
        return ActionIntent(random_action, arguments)

        



