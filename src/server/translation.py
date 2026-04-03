from gameengine.priority.event import EventData
from gameengine.player import PlayerInfo
from server.api.gym_types import MtgObservation, MtgAction, MtgPlayerObs
from gameengine.state import GameState
from gameengine.constants import Action
from gameengine.priority.event import PlayerEvent
from gameengine.cards.model.catalog import CARD_CATALOG

from logging_config import api_log as logger

def game_state_to_obs(state: GameState, agent_position: int) -> MtgObservation:
    player_info: PlayerInfo = state.player_infos[agent_position]
    #Assume two players for the momement
    opponent_info: PlayerInfo = state.player_infos[(agent_position + 1) % 2]
    result: MtgObservation = (
        event_to_index(state.upcoming_event), #upcoming_decision
        int(state.active_player_index == agent_position), #agent_is_active_player
        agent_position, #agent_seat_position
        player_obs_from_info(player_info), #agent_status 
        player_obs_from_info(opponent_info), #opponents_status
    )
    return result

def event_to_index(event: PlayerEvent) -> int:
    match event:
        case PlayerEvent.MAIN_PHASE_EMPTY_STACK:
            return 0
        case PlayerEvent.DECLARE_ATTACKS:
            return 1 

def gym_action_to_priority_decision(upcoming_event: EventData, action: MtgAction) -> Action:
    logger.debug("Translating for decision [{}]".format(upcoming_event))
    intent: Action = upcoming_event.possible_actions[action[0]]
    logger.debug("Translated external action {} into internal intent [{}]".format(action[0], intent))
    return intent

def player_obs_from_info(player_info: PlayerInfo) -> MtgPlayerObs:
    #
    return (
        player_info.current_life, #hp
        len(player_info.cards_in_hand), #cards_in_hand
        player_info.cards_in_library #cards_in_library
    )

def card_index_to_name(index: int) -> str:
    card_names: list[str] = sorted(CARD_CATALOG)
    return card_names[min(index, len(card_names) - 1)]

def card_name_to_index(name: str) -> int:
    card_names: list[str] = sorted(CARD_CATALOG)
    return card_names.index(name)