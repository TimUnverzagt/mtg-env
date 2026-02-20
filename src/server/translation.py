from gameengine.priority.base import DECISION_EVENT_CATALOG, PriorityEvent
from gameengine.player import PlayerInfo
from server.api.gym_types import MtgObservation, MtgAction, MtgPlayerObs
from gameengine.state import GameState

from logging_config import api_log as logger

def game_state_to_obs(state: GameState, agent_position: int) -> MtgObservation:
    player_info: PlayerInfo = state.player_infos[agent_position]
    #Assume two players for the momement
    opponent_info: PlayerInfo = state.player_infos[(agent_position + 1) % 2]
    result: MtgObservation = (
        DECISION_EVENT_CATALOG.index(state.upcoming_decision), #upcoming_decision
        int(state.active_player_index == agent_position), #agent_is_active_player
        agent_position, #agent_seat_position
        player_obs_from_info(player_info), #agent_status 
        player_obs_from_info(opponent_info), #opponents_status
    )
    return result

def gym_action_to_priority_decision(upcoming_event: PriorityEvent, action: MtgAction) -> str:
    logger.debug("Translating for decision [{}]".format(upcoming_event))
    intent: str = upcoming_event.possible_actions[action[0]]
    logger.debug("Translated external action {} into internal intent [{}]".format(action[0], intent))
    return intent

def player_obs_from_info(player_info: PlayerInfo) -> MtgPlayerObs:
    #
    return (
        player_info.current_life, #hp
        len(player_info.cards_in_hand), #cards_in_hand
        player_info.cards_in_library #cards_in_library
    )