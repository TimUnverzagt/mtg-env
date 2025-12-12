from server.multi_client_session import MultiClientSession as GameSession
from game.decision_event import DecisionEvent
#import environment.constants as EnvConsts
from agents.abstractions.base import AgentBase

from package.logging_config import main_log
import random
import sys

class Goldfish(AgentBase):
    def __init__(self, session: GameSession, target_seat: int | None =  None) -> None:
        super().__init__(session, target_seat)

    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        neutral_index: int = upcoming_action.neutral_action_index
        return upcoming_action.possible_actions[neutral_index]
    
class Monkey(AgentBase):
    def __init__(self, session: GameSession, target_seat: int | None =  None) -> None:
        super().__init__(session, target_seat)
        seed: int = random.randrange(sys.maxsize)  
        self.random_generator = random.Random(seed)
        main_log.info("Random seed for monkey: {}".format(seed))

    def decide_on_action(self, upcoming_action: DecisionEvent) -> str:
        random_index: int = self.random_generator.randint(0, len(upcoming_action.possible_actions) - 1)
        return upcoming_action.possible_actions[random_index]

        



