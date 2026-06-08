from server.session.multi_client_session import MultiClientSession as GameSession
from gameengine.priority.event import EventData
from gameengine.constants import Action
#import environment.constants as EnvConsts
from server.agents.abstractions.base import AgentBase

from config.logging_config import main_log
import random
import sys

class Goldfish(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)

    def decide_on_action(self, upcoming_action: EventData) -> Action:
        neutral_index: int = upcoming_action.neutral_action_index
        return upcoming_action.possible_actions[neutral_index]
    
class Monkey(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)
        seed: int = random.randrange(sys.maxsize)  
        self.random_generator = random.Random(seed)
        main_log.info("Random seed for monkey: {}".format(seed))

    def decide_on_action(self, upcoming_action: EventData) -> Action:
        random_index: int = self.random_generator.randint(0, len(upcoming_action.possible_actions) - 1)
        return upcoming_action.possible_actions[random_index]

        



