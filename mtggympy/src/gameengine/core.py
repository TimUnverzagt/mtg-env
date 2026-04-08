from __future__ import annotations
from collections import defaultdict
from gameengine.constants import Action, ManaColor, Zone
import gameengine.constants as const
from gameengine.player import Player, PlayerInfo, is_player_alive
from gameengine.priority.event import PlayerEvent
from gameengine.gameobjects import CardInstance
from gameengine.state import GameState
from gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from gameengine.cards.info import CardInfo, SpellInfo
from gameengine.cards.catalog.full import CARD_CATALOG
from gameengine.capabilities import ManaProvider

from helpers.dict_operations import first_dict_can_fit_second_by_value
from typing import Callable, Generic, Optional, ParamSpec, TypeVar, Any, Concatenate

from logging_config import engine_log as logger

def get_initial_game_state() -> GameState:
    player1: Player = Player("Player1")
    player2: Player = Player("Player2")
    game_state: GameState = GameState(
        player_turns_completed = 0,
        active_player_index = 0,
        game_over = False,
        upcoming_event=PlayerEvent.MAIN_PHASE_EMPTY_STACK,
        player_infos = [player1.info, player2.info],
        winner_positions=[],
        floating_mana=defaultdict(lambda: 0)
    )
    return game_state

#def is_legal_action(decision_intent: str, game_state: GameState) -> bool:
#    return True

def step(acting_seat: int, decision_intent: Action, game_state: GameState, decision_details : Optional[dict[str, Any]] = None) -> None:
    # Don't respond if the game is over
    if(game_state.game_over):
        return
    
    # Handle decision of step
    logger.info("Handling intent '{}' for player event '{}' from {}".format(
        decision_intent, game_state.upcoming_event.name, game_state.player_infos[acting_seat].name
        ))
    match game_state.upcoming_event:
        case PlayerEvent.MAIN_PHASE_EMPTY_STACK:
            handle_main_phase_decision(acting_seat, decision_intent, game_state, decision_details)
        case PlayerEvent.DECLARE_ATTACKS:
            handle_combat_decision(acting_seat, decision_intent, game_state)
    return 

def handle_main_phase_decision(acting_seat: int, decision: Action, game_state: GameState, decision_details : Optional[dict[str, Any]] = None) -> None:
    match decision:
        case Action.PASS:
            empty_mana_pool(game_state)
            game_state.upcoming_event = PlayerEvent.DECLARE_ATTACKS
        case Action.PLAY_CARD:
            if(decision_details is None):
                # TODO: Raise and handle error
                logger.error(const.CARD_TO_PLAY+ ": Details are missing. Refusing to process intent!")
                return
            card_name = decision_details[const.CARD_TO_PLAY]
            if (not isinstance(card_name, str)): # type: ignore
                logger.error(const.CARD_TO_PLAY+ ": Non string object in details. Refusing to process intent!")
                return
            logger.info("Trying to play CardInstance with name: " + str(card_name)); # type: ignore
            play_card(acting_seat, game_state, card_name)
        case Action.ACTIVATE_LANDS:
            activate_lands(acting_seat, game_state)
        case _:
            handle_illegal_action(decision, PlayerEvent.MAIN_PHASE_EMPTY_STACK)
    return

def activate_lands(acting_seat: int, game_state:GameState):
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to activate lands. Refusing to process intent!")
        return
    cards_on_active_board: list[CardInstance] = game_state.player_infos[acting_seat].cards_in_play
    new_mana: list[ManaColor] = []
    for card in cards_on_active_board:
        if not isinstance(card, ManaProvider):
            continue
        if not card.is_ready():
            continue
        new_mana += card.produce_mana()
    for color in new_mana:
        game_state.floating_mana[color] += 1
    return

def play_card(acting_seat: int, game_state:GameState, card_name: str):
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to play a card. Refusing to process intent!")
        return
    hand: list[CardInstance] = game_state.player_infos[acting_seat].cards_in_hand
    battlefield: list[CardInstance] = game_state.player_infos[acting_seat].cards_in_play
    card_info: Optional[CardInfo] = CARD_CATALOG.get(card_name)
    if card_info is None:
        logger.error("Player on seat {} is trying to play {} which isn't a known card. Refusing to process intent".format(
            acting_seat, card_name
        ))
        return
    card_to_play: Optional[CardInstance] = None
    for card in hand:
        if card.card_name == card_name:
            card_to_play = card
            break
    if card_to_play is None:
        logger.error("Player on seat {} is trying to play {} without having a copy in hand. Refusing to process intent".format(
            acting_seat, card_name
        ))
        return
    
    if isinstance(card_info, SpellInfo):
        if not first_dict_can_fit_second_by_value(game_state.floating_mana, card_info.mana_cost):
            logger.error("Player on seat {} is trying to play {} without having enough mana. Refusing to process intent".format(
                acting_seat, card_name
            ))
            logger.info("Available mana: {}".format(game_state.floating_mana)) 
            logger.info("Required mana: {}".format(card_info.mana_cost))
            return
        for color in card_info.mana_cost:
            game_state.floating_mana[color] -= card_info.mana_cost[color]

    hand.remove(card_to_play)
    battlefield.append(card_to_play)
    card_to_play.zone = Zone.BATTLEFIELD
    return

def handle_combat_decision(acting_seat: int, decision: Action, game_state: GameState) -> None:
    match decision:
        case Action.PASS:
            pass_turn(game_state)
        case Action.ATTACK:
            logger.warning("Turn {}/{}: {} is attacking!".format(
                game_state.player_turns_completed,
                len(game_state.player_infos),
                game_state.player_infos[acting_seat].name)
            )

            # Just use the only other player as target until multiplayer is implemented
            defending_position: int =(game_state.active_player_index + 1) % len(game_state.player_infos)
            # Just decrease health by flat amount for poc
            execute_action(acting_seat, game_state, deal_damage, defending_position, 1)
            pass_turn(game_state)
        case _:
            handle_illegal_action(decision, PlayerEvent.DECLARE_ATTACKS)
    return

def handle_illegal_action(action: Action, event: PlayerEvent) -> None:
    logger.error("Action '{}' not legal for event {}. Refusing to process intent.".format(
        action.name,
        event.name
    ))
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

def empty_mana_pool(game_state: GameState) -> None:
    game_state.floating_mana = defaultdict(lambda: 0)

def pass_turn(game_state: GameState) -> None:
    # complete old turn
    game_state.player_turns_completed += 1
    next_active_seat: int = (game_state.active_player_index + 1) % len(game_state.player_infos)
    game_state.active_player_index = next_active_seat

    # Handle setup of new turn
    logger.info("{} will draw a card for turn".format(game_state.player_infos[next_active_seat].name))
    execute_action(next_active_seat, game_state, draw_card)
    game_state.upcoming_event = PlayerEvent.MAIN_PHASE_EMPTY_STACK

def get_player_position(info: PlayerInfo, game_state:GameState) -> int:
    return game_state.player_infos.index(info)

##################################    
# Actions to be handled by proxy
##################################

def draw_card(acting_seat: int, game_state: GameState) -> None:
    hand: list[CardInstance] = game_state.player_infos[acting_seat].cards_in_hand
    library: list[CardInstance] = game_state.player_infos[acting_seat].cards_in_library
    # Decking is handled prior
    card_drawn: CardInstance = library.pop(0)
    hand.append(card_drawn)
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
    and not game_state.player_infos[acting_seat].cards_in_library:
        return replacement_catalog[const.DECKING].replacing_action(acting_seat, game_state, *args, **kwargs)
        
    return attempted_action(acting_seat, game_state, *args, **kwargs)
    
def execute_action(acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                    *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
    action_result: ActionResult = _execute_action_with_replacment(acting_seat, game_state, attempted_action, *args, **kwargs)
    check_state_based_actions(game_state)
    return action_result

