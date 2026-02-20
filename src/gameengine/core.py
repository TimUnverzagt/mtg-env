from __future__ import annotations
import gameengine.constants as const
from gameengine.player import Player, PlayerInfo, is_player_alive
from gameengine.priority.base import PriorityEvent, DECISION_EVENT_CATALOG
from gameengine.card import CardInstance
from gameengine.state import GameState
from typing import Callable, Generic, Optional, ParamSpec, TypeVar, Any, Concatenate, cast
from uuid import UUID

from logging_config import engine_log as logger

def get_initial_game_state() -> GameState:
    player1: Player = Player("Player1")
    player2: Player = Player("Player2")
    game_state: GameState = GameState(
        player_turns_completed = 0,
        steps_in_turn_completed = 0,
        active_player_index = 0,
        game_over = False,
        upcoming_decision=DECISION_EVENT_CATALOG[0],
        player_infos = [player1.info, player2.info],
        winner_positions=[]
    )
    return game_state

#def is_legal_action(decision_intent: str, game_state: GameState) -> bool:
#    return True

def step(acting_seat: int, decision_intent: str, game_state: GameState, decision_details : Optional[dict[str, Any]] = None) -> None:
    # Don't respond if the game is over
    if(game_state.game_over):
        return
        
    acting_player_info: PlayerInfo = game_state.player_infos[acting_seat]
    applicable_decision: PriorityEvent = get_upcoming_decision(game_state)

    # Handle decision of step
    # TODO: How to handle exceptions/enforcement for nonsensical decision inputs
    logger.info("Handling intent '{}' for decision event '{}' from {}".format(
        decision_intent, applicable_decision.name, acting_player_info.name
        ))
    if (applicable_decision.name == const.COMBAT):
        handle_combat_decision(acting_seat, decision_intent, game_state)
    if (applicable_decision.name == const.MAINPHASE):
        handle_main_phase_decision(acting_seat, decision_intent, game_state, decision_details)
    # Stop immediatly if game is over now
    if(game_state.game_over):
        return
        
    game_state.steps_in_turn_completed += 1
    if(game_state.steps_in_turn_completed >= len(DECISION_EVENT_CATALOG)):
        pass_turn(game_state)
    return 

def handle_main_phase_decision(acting_seat: int, decision: str, game_state: GameState, decision_details : Optional[dict[str, Any]] = None) -> None:
    if(decision==const.MAINPHASE_PASS):
        return
    if(decision_details is None):
        # TODO: Raise and handle error
        logger.warning(const.CARDS_TO_PLAY+ ": Details are missing. NoOp instead!")
        return
    cards_to_play = decision_details[const.CARDS_TO_PLAY]
    assert isinstance(cards_to_play, list)
    if (not all(isinstance(card_id, UUID) for card_id in cards_to_play)): # type: ignore
        # TODO: Raise and handle error
        logger.warning(const.CARDS_TO_PLAY+ ": Non UUID object in details. NoOp instead!")
        return
    for card_id in cards_to_play: # type: ignore
        cast(UUID, card_id)
        logger.info("Trying to play CardInstance with UUID: " + str(card_id)); # type: ignore
    
    return

def handle_combat_decision(acting_seat: int, decision: str, game_state: GameState) -> None:
    if(decision==const.COMBAT_PASS):
        return
    
    logger.warning("Turn {}/{}: {} is attacking!".format(
        game_state.player_turns_completed,
        len(game_state.player_infos),
        game_state.player_infos[acting_seat].name)
    )
    # Just use the only other player as target
    defending_position: int =(game_state.active_player_index + 1) % len(game_state.player_infos)
    # Just decrease health by flat amount for poc
    execute_action(acting_seat, game_state, deal_damage, defending_position, 1)
    return

def check_state_based_actions(game_state: GameState) -> None:
    logger.debug("Checking state-based effects")
    check_player_death(game_state)
    check_for_game_end(game_state)
    return

def check_player_death(game_state: GameState) -> None:
    alive_player_infos: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_infos))
    players_dying_from_hp: list[PlayerInfo] = list(filter(lambda player_info: player_info.current_life <= 0, alive_player_infos))
    if len(players_dying_from_hp) > 0:
        for player_info in players_dying_from_hp:
            handle_player_death(get_player_position(player_info, game_state), game_state, "having 0 or less life");
   

def check_for_game_end(game_state: GameState):
    surviving_players: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_infos))
    if len(surviving_players) <= 1:
        game_state.game_over = True
        logger.info("Game ended by death of player(s)")
    if len(surviving_players) == 1:
        game_state.winner_positions = [game_state.player_infos.index(surviving_players[0])]
        logger.info("{} won by survival".format(surviving_players[0].name))

def kill_player_by_decking(victim_seat: int, game_state: GameState) -> None:
    handle_player_death(victim_seat, game_state, "drawing from an empty library")
    return
    
def handle_player_death(victim_seat: int, game_state: GameState, cause: str):
    game_state.player_infos[victim_seat].death_description = cause
    logger.warning("{} died by {}.".format(game_state.player_infos[victim_seat].name, cause))
    return
    
def get_upcoming_decision(game_state: GameState) -> PriorityEvent:
    return DECISION_EVENT_CATALOG[game_state.steps_in_turn_completed]

def pass_turn(game_state: GameState) -> None:
    # complete old turn
    game_state.player_turns_completed += 1
    game_state.steps_in_turn_completed = 0
    next_active_seat: int = (game_state.active_player_index + 1) % len(game_state.player_infos)
    game_state.active_player_index = next_active_seat

    # Handle setup of new turn
    logger.info("{} will draw a card for turn".format(game_state.player_infos[next_active_seat].name))
    execute_action(next_active_seat, game_state, draw_card)

def get_player_position(info: PlayerInfo, game_state:GameState) -> int:
    return game_state.player_infos.index(info)

##################################    
# Actions to be handled by proxy
##################################

def draw_card(acting_seat: int, game_state: GameState) -> None:
    game_state.player_infos[acting_seat].cards_in_hand.append(CardInstance(3))
    # Decking is handled prior
    game_state.player_infos[acting_seat].cards_in_library -= 1
    return
    
def deal_damage(acting_seat: int, game_state: GameState, target_seat:int, damage_amount:int) -> None:
    game_state.player_infos[target_seat].current_life -= damage_amount
    return    

##################################
# Action proxy
##################################

AdditionalParam = ParamSpec("AdditionalParam")
ActionResult = TypeVar("ActionResult")

class ActionReplacement(Generic[AdditionalParam, ActionResult]):

    def __init__(self,
                 input_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult],
                 replacing_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult]):
        self.input_action = input_action
        self.replacing_action = replacing_action
        return

replacement_catalog: dict[str, ActionReplacement[Any, Any]] = {
    const.DECKING: ActionReplacement(draw_card, kill_player_by_decking)
}

def _execute_action_with_replacment(acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                    *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
        
    if attempted_action == replacement_catalog[const.DECKING].input_action \
    and game_state.player_infos[acting_seat].cards_in_library <= 0:
        return replacement_catalog[const.DECKING].replacing_action(acting_seat, game_state, *args, **kwargs)
        
    return attempted_action(acting_seat, game_state, *args, **kwargs)
    
def execute_action(acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                    *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
    action_result: ActionResult = _execute_action_with_replacment(acting_seat, game_state, attempted_action, *args, **kwargs)
    check_state_based_actions(game_state)
    return action_result

