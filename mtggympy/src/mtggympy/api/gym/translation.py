import math
from typing import cast

import numpy as np

from mtggympy.gameengine.cards.instances.types import CardInstance, CreatureInstance
from mtggympy.gameengine.state.event import ActionIntent, PlayerEvent
from mtggympy.api.gym.encoding import MtgCardObs, MtgObservation, MtgAction, MtgOppObs, MtgSelfObs
import mtggympy.api.gym.encoding as encode
from mtggympy.gameengine.state.event import PlayerEvent
from mtggympy.gameengine.cards.catalog.lookup import FULL_CATALOG

from mtggympy.config.logging_config import api_log as logger
from mtggympy.helpers.tree_map import tree_map
from mtggympy.server.session.observed_state import ObservedGameState, ObservedSelfState, ObservedOpponentState

def observed_state_to_obs(state: ObservedGameState, observation_limits: MtgObservation | None = None) -> MtgObservation:
    #Assume two players for the momement
    opponent_state: ObservedOpponentState = state.opponent_states[0]
    obs: MtgObservation = (
        state.seat_position,
        math.floor(state.halfturns_completed / 2),
        event_to_index(state.event), #upcoming_decision
        int(state.self_is_active_player), #agent_is_active_player
        self_obs_from_state(state.self_state), #agent_status 
        opp_obs_from_state(opponent_state), #opponents_status
    )
    if observation_limits:
        obs = cast(MtgObservation, tree_map(min, obs, observation_limits))
    return obs

def event_to_index(event: PlayerEvent) -> int:
    match event:
        case PlayerEvent.MAINPHASE_EMPTY_STACK:
            return 0
        case PlayerEvent.DECLARE_ATTACKS:
            return 1 
        case PlayerEvent.DECLARE_BLOCKS:
            return 2
        case PlayerEvent.NO_OP:
            return 3

def gym_action_to_player_decision(upcoming_event: PlayerEvent, action: MtgAction) -> ActionIntent:
    logger.debug("Translating for decision [{}]".format(upcoming_event))
    #TODO: Get params as well
    action_index: int = int(action[0])
    if(action_index >= len(upcoming_event.value.possible_actions)):
        action_index = 0
    intent: ActionIntent = ActionIntent(upcoming_event.value.possible_actions[action_index],None)
    logger.debug("Translated external action {} into internal intent [{}]".format(action_index, intent))
    return intent

def self_obs_from_state(self_state: ObservedSelfState) -> MtgSelfObs:
    return (
        self_state.current_life, #hp
        self_state.cards_in_library, #cards_in_library
        card_obs_from_instances(self_state.cards_in_hand, encode.ASSUMED_MAX_HAND_SIZE), #cards_in_hand
        card_obs_from_instances(self_state.cards_in_play, encode.ASSUMED_MAX_BATTLEFIELD_SIZE), #cards in play
    )
def opp_obs_from_state(opp_state: ObservedOpponentState) -> MtgOppObs:
    return (
        opp_state.current_life, #hp
        opp_state.cards_in_library, #cards_in_library
        opp_state.cards_in_hand, #cards_in_hand
        card_obs_from_instances(opp_state.cards_in_play, encode.ASSUMED_MAX_BATTLEFIELD_SIZE), #cards in play
    )

def card_obs_from_instances(cards: list[CardInstance], target_encoding_len: int) -> np.ndarray:
    card_obs: list[MtgCardObs] = []
    for i in range(0, target_encoding_len):
        if i >= len(cards):
            card_obs.append(np.array([0, 0, 0]))
            continue
        card = cards[i]
        card_attacking: bool = False
        if isinstance(CardInstance, CreatureInstance):
            assert card is CreatureInstance
            card_attacking = card.attacking
        card_obs.append(np.array([
            card_name_to_index(card.card_name) + 1, # Leave null index for empty space
            int(card.tapped),
            int(card_attacking)
        ]))
    return np.stack(card_obs)

def card_index_to_name(index: int) -> str:
    card_names: list[str] = sorted(FULL_CATALOG)
    return card_names[min(index, len(card_names) - 1)]

def card_name_to_index(name: str) -> int:
    card_names: list[str] = sorted(FULL_CATALOG)
    return card_names.index(name)
