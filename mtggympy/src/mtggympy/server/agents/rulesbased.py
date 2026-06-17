
from mtggympy.gameengine.constants import CardType
from mtggympy.gameengine.gameobjects import CardInstance, CreatureInstance, LandInstance
from mtggympy.helpers.dict_operations import first_dict_can_fit_second_by_value
from mtggympy.server.agents.abstractions.base import AgentBase

from mtggympy.server.session.multi_client_session import MultiClientSession as GameSession
from mtggympy.gameengine.priority.event import ActionData, ActionIntent, PlayerEvent
from mtggympy.server.session.observed_state import ObservedGameState

import numpy as np

class RulesBasedAgent(AgentBase):
    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None) -> None:
        super().__init__(session, name, target_seat)

    def decide_on_action(self, upcoming_action: PlayerEvent) -> ActionIntent:
        neutral_index: int = upcoming_action.value.neutral_action_index
        if self.controller is None or self.controller.obs_before_action is None:
            return ActionIntent(upcoming_action.value.possible_actions[neutral_index], None)
        match upcoming_action:
            case PlayerEvent.MAINPHASE_EMPTY_STACK:
                return self.decide_on_mainphase_action(upcoming_action, self.controller.obs_before_action)
            case _:
                return ActionIntent(upcoming_action.value.possible_actions[neutral_index], None)
    
    def decide_on_mainphase_action(self, upcoming_action: PlayerEvent, observations: ObservedGameState) -> ActionIntent:
        #play land if able
        if(observations.lands_played_this_turn < 1):
            for idx, card in enumerate(observations.self_state.cards_in_hand):
                if card.type is CardType.LAND:
                    return ActionIntent(ActionData.PLAY_CARD, np.array(idx))
        tappable_lands_idx: list[list[int]] = []
        lands: list[CardInstance] = list(filter(lambda card: isinstance(card, LandInstance),observations.self_state.cards_in_play))
        for idx, card in enumerate(lands):
            if not card.tapped:
                tappable_lands_idx.append([idx])
        if len(tappable_lands_idx) > 0:
            return ActionIntent(ActionData.ACTIVATE_LANDS, np.array(tappable_lands_idx))
        for idx, card in enumerate(observations.self_state.cards_in_hand):
            if not isinstance(card, CreatureInstance):
                continue
            if not first_dict_can_fit_second_by_value(observations.self_state.floating_mana, card.mana_cost):
                continue
            return ActionIntent(ActionData.PLAY_CARD, np.array(idx))
        return ActionIntent(ActionData.PASS, None)
