from server.multi_client_session import MultiClientSession as GameSession
from environment.action_event import ActionEvent
import environment.constants as EnvConsts
from agents.abstractions.base import AgentBase

import logging
logger = logging.getLogger(__name__)

class Goldfish(AgentBase):
    def __init__(self, session: GameSession) -> None:
        super().__init__(session)

    def decide_on_action(self, upcoming_action: ActionEvent) -> str:
        if upcoming_action.name == EnvConsts.COMBAT:
            return EnvConsts.COMBAT_PASS
        if upcoming_action.name == EnvConsts.MAINPHASE:
            return EnvConsts.MAINPHASE_PASS
        return "Confused noises"

        



