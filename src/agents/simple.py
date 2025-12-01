from server.multi_client_session import MultiClientSession as GameSession
from environment.action_event import ActionEvent
import environment.constants as EnvConsts
from agents.abstractions.base import AgentBase

from logging_config import main_log
import random
import sys

class Goldfish(AgentBase):
    def __init__(self, session: GameSession) -> None:
        super().__init__(session)

    def decide_on_action(self, upcoming_action: ActionEvent) -> str:
        if upcoming_action.name == EnvConsts.COMBAT:
            return EnvConsts.COMBAT_PASS
        if upcoming_action.name == EnvConsts.MAINPHASE:
            return EnvConsts.MAINPHASE_PASS
        return "Confused noises"
    
class Monkey(AgentBase):
    def __init__(self, session: GameSession) -> None:
        super().__init__(session)
        seed: int = random.randrange(sys.maxsize)  
        self.random_generator = random.Random(seed)
        main_log.info("Random seed for monkey: {}".format(seed))

    def decide_on_action(self, upcoming_action: ActionEvent) -> str:
        random_index: int = self.random_generator.randint(0, len(upcoming_action.possible_actions) - 1)
        return upcoming_action.possible_actions[random_index]

        



