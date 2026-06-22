from mtggympy.gameengine.state.event import ActionIntent, PlayerEvent, event_from_step
from mtggympy.api.gym.types import MtgObservation, MtgAction, MtgPlayerObs
from mtggympy.gameengine.state.event import PlayerEvent
from mtggympy.gameengine.cards.catalog.lookup import FULL_CATALOG

from mtggympy.logging_config import api_log as logger
from mtggympy.server.session.observed_state import ObservedGameState, ObservedSelfState, ObservedOpponentState

def observed_state_to_obs(state: ObservedGameState, agent_position: int) -> MtgObservation:
    #Assume two players for the momement
    opponent_state: ObservedOpponentState = state.opponent_states[(agent_position + 1) % 2]
    result: MtgObservation = (
        event_to_index(event_from_step(state.step)), #upcoming_decision
        int(state.self_is_active_player), #agent_is_active_player
        agent_position, #agent_seat_position
        player_obs_from_self(state.self_state), #agent_status 
        player_obs_from_opponent(opponent_state), #opponents_status
    )
    return result

def event_to_index(event: PlayerEvent) -> int:
    match event:
        case PlayerEvent.MAINPHASE_EMPTY_STACK:
            return 0
        case PlayerEvent.DECLARE_ATTACKS:
            return 1 
        case PlayerEvent.NO_OP:
            return 2

def gym_action_to_priority_decision(upcoming_event: PlayerEvent, action: MtgAction) -> ActionIntent:
    logger.debug("Translating for decision [{}]".format(upcoming_event))
    #TODO: Get params as well
    intent: ActionIntent = ActionIntent(upcoming_event.value.possible_actions[action[0]],None)
    logger.debug("Translated external action {} into internal intent [{}]".format(action[0], intent))
    return intent

def player_obs_from_self(state: ObservedSelfState) -> MtgPlayerObs:
    #
    return (
        state.current_life, #hp
        len(state.cards_in_hand), #cards_in_hand
        state.cards_in_library #cards_in_library
    )
def player_obs_from_opponent(state: ObservedOpponentState) -> MtgPlayerObs:
    #
    return (
        state.current_life, #hp
        state.cards_in_hand, #cards_in_hand
        state.cards_in_library #cards_in_library
    )

def card_index_to_name(index: int) -> str:
    card_names: list[str] = sorted(FULL_CATALOG)
    return card_names[min(index, len(card_names) - 1)]

def card_name_to_index(name: str) -> int:
    card_names: list[str] = sorted(FULL_CATALOG)
    return card_names.index(name)