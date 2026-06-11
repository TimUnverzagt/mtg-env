from mtggympy.server.session.multi_client_session import MultiClientSession as GameSession
from mtggympy.gameengine.priority.event import ActionIntent, EventData
#import environment.constants as EnvConsts
from mtggympy.server.agents.abstractions.base import AgentBase

from mtggympy.logging_config import main_log
import random
import sys

class Goldfish(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)

    def decide_on_action(self, upcoming_action: EventData) -> ActionIntent:
        neutral_index: int = upcoming_action.neutral_action_index
        return ActionIntent(upcoming_action.possible_actions[neutral_index], None)
    
class Monkey(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)
        seed: int = random.randrange(sys.maxsize)  
        self.random_generator = random.Random(seed)
        main_log.info("Random seed for monkey: {}".format(seed))

    def decide_on_action(self, upcoming_action: EventData) -> ActionIntent:
        random_index: int = self.random_generator.randint(0, len(upcoming_action.possible_actions) - 1)
        # TODO: Respect Action dimensionality
        return ActionIntent(upcoming_action.possible_actions[random_index], None)

        



