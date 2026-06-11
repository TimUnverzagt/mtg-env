from __future__ import annotations
from collections import defaultdict
from mtggympy.gameengine.constants import ManaColor, Zone
import mtggympy.gameengine.constants as const
from mtggympy.gameengine.player import Player
from mtggympy.gameengine.priority.event import ActionIntent, PlayerEvent, ActionData
from mtggympy.gameengine.gameobjects import CardInstance, CardType
from mtggympy.gameengine.state import GameState, PlayerState, is_player_alive
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from mtggympy.gameengine.capabilities import ManaProvider

from mtggympy.helpers.dict_operations import first_dict_can_fit_second_by_value
from typing import Callable, Generic, Optional, ParamSpec, TypeVar, Any, Concatenate

from mtggympy.logging_config import engine_log as logger

def get_initial_game_state() -> GameState:
    player1: Player = Player("Player1")
    player2: Player = Player("Player2")
    game_state: GameState = GameState(
        halfturns_completed = 0,
        active_player_index = 0,
        game_over = False,
        upcoming_event=PlayerEvent.MAIN_PHASE_EMPTY_STACK,
        player_states = [player1.info, player2.info],
        winner_positions=[]
    )
    return game_state

#def is_legal_action(decision_intent: str, game_state: GameState) -> bool:
#    return True

def step(acting_seat: int, decision_intent: ActionIntent, game_state: GameState, decision_details : Optional[dict[str, Any]] = None) -> None:
    # Don't respond if the game is over
    if(game_state.game_over):
        return
    
    # Handle decision of step
    logger.info("Handling intent '{}' for player event '{}' from {}".format(
        decision_intent, game_state.upcoming_event.name, game_state.player_states[acting_seat].name
        ))
    match game_state.upcoming_event:
        case PlayerEvent.MAIN_PHASE_EMPTY_STACK:
            handle_main_phase_decision(acting_seat, decision_intent, game_state)
        case PlayerEvent.DECLARE_ATTACKS:
            handle_combat_decision(acting_seat, decision_intent.action, game_state)
    return 

def handle_main_phase_decision(acting_seat: int, intent: ActionIntent, game_state: GameState) -> None:
    match intent.action:
        case ActionData.PASS:
            empty_mana_pool(game_state)
            game_state.upcoming_event = PlayerEvent.DECLARE_ATTACKS
        case ActionData.PLAY_CARD:
            target_card: CardInstance|None = try_selecting_card_for_playing(acting_seat, intent, game_state)
            if target_card is None:
                return
            play_card(acting_seat, game_state, target_card)
        case ActionData.ACTIVATE_LANDS:
            target_lands: list[CardInstance] | None = try_selecting_lands_for_activation(acting_seat, intent, game_state)
            if target_lands is None:
                return
            activate_lands(acting_seat, game_state, target_lands)
        case _:
            handle_illegal_action(intent.action, PlayerEvent.MAIN_PHASE_EMPTY_STACK)
    return

def try_selecting_card_for_playing(acting_seat: int, intent: ActionIntent, game_state: GameState) -> CardInstance | None:
    if(intent.parameters is None):
        logger.error("{}: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if(intent.parameters.size != 1):
        logger.error("{}: More than one argument. Refusing to process intent!".format(intent.action.name))
        return None
    card_index: int = intent.parameters.sum() # This colapses various shapes
    if(card_index >= len(game_state.player_states[acting_seat].cards_in_hand)):
        logger.error("{}: No card at given position. Refusing to process intent!".format(intent.action.name))
        return None
    return game_state.player_states[acting_seat].cards_in_hand[card_index]

def try_selecting_lands_for_activation(acting_seat: int, intent: ActionIntent, game_state: GameState) -> list[CardInstance] | None:
    if(intent.parameters is None):
        logger.error("{}: Arguments are missing. Refusing to process intent!".format(intent.action.name))
        return None
    if(intent.parameters.shape[1] != 1):
        logger.error("{}: Arguments. Refusing to process intent!".format(intent.action.name))
        return None
    existing_lands: list[CardInstance] = list(filter(lambda card: card.type is CardType.LAND ,game_state.player_states[acting_seat].cards_in_play))
    target_lands: list[CardInstance] = []
    for index in intent.parameters:
        if (index >= len(existing_lands)):
            logger.error("{}: No card at given position. Refusing to process intent!".format(intent.action.name))
            return None
        target_lands.append(existing_lands[int(index[0])])
    return target_lands
    


def activate_lands(acting_seat: int, game_state:GameState, target_lands: list[CardInstance]):
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to activate lands. Refusing to process intent!")
        return
    new_mana: list[ManaColor] = []
    for card in target_lands:
        if not isinstance(card, ManaProvider):
            logger.error("Target land {} is not a mana provider. Refusing to process intent!".format(card.card_name))
            return
        if not card.is_ready():
            logger.error("Target land {} is not ready. Refusing to process intent!".format(card.card_name))
        new_mana += card.produce_mana()
    for color in new_mana:
        game_state.player_states[acting_seat].floating_mana[color] += 1
    return

def play_card(acting_seat: int, game_state:GameState, card: CardInstance):
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to play a card. Refusing to process intent!")
        return
    hand: list[CardInstance] = game_state.player_states[acting_seat].cards_in_hand
    battlefield: list[CardInstance] = game_state.player_states[acting_seat].cards_in_play
    floating_mana: dict[ManaColor, int] = game_state.player_states[acting_seat].floating_mana

    if card.type in [CardType.CREATURE]:
        assert card.mana_cost is not None
        if not first_dict_can_fit_second_by_value(floating_mana, card.mana_cost):
            logger.error("Player on seat {} is trying to play {} without having enough mana. Refusing to process intent".format(
                acting_seat, card.card_name
            ))
            logger.debug("Available mana: {}".format(floating_mana)) 
            logger.debug("Required mana: {}".format(card.mana_cost))
            logger.debug("Cards in hand: {}".format(list(map(lambda card: card.card_name, hand))))
            return
        for color in card.mana_cost:
            floating_mana[color] -= card.mana_cost[color]

    hand.remove(card)
    battlefield.append(card)
    card.zone = Zone.BATTLEFIELD
    return

def handle_combat_decision(acting_seat: int, decision: ActionData, game_state: GameState) -> None:
    match decision:
        case ActionData.PASS:
            pass_turn(game_state)
        case ActionData.ATTACK:
            logger.warning("Turn {}/{}: {} is attacking!".format(
                game_state.halfturns_completed,
                len(game_state.player_states),
                game_state.player_states[acting_seat].name)
            )

            # Just use the only other player as target until multiplayer is implemented
            defending_position: int =(game_state.active_player_index + 1) % len(game_state.player_states)
            # Just decrease health by flat amount for poc
            execute_action(acting_seat, game_state, deal_damage, defending_position, 1)
            pass_turn(game_state)
        case _:
            handle_illegal_action(decision, PlayerEvent.DECLARE_ATTACKS)
    return

def handle_illegal_action(action: ActionData, event: PlayerEvent) -> None:
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
    alive_player_infos: list[PlayerState] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_states))
    players_dying_from_hp: list[PlayerState] = list(filter(lambda player_info: player_info.current_life <= 0, alive_player_infos))
    if len(players_dying_from_hp) > 0:
        for player_info in players_dying_from_hp:
            handle_player_death(get_player_position(player_info, game_state), game_state, "having 0 or less life");
   

def check_for_game_end(game_state: GameState):
    surviving_players: list[PlayerState] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_states))
    if len(surviving_players) <= 1:
        game_state.game_over = True
        logger.info("Game ended by death of player(s)")
    if len(surviving_players) == 1:
        game_state.winner_positions = [game_state.player_states.index(surviving_players[0])]
        logger.info("{} won by survival".format(surviving_players[0].name))

def kill_player_by_decking(victim_seat: int, game_state: GameState) -> None:
    handle_player_death(victim_seat, game_state, "drawing from an empty library")
    return
    
def handle_player_death(victim_seat: int, game_state: GameState, cause: str):
    game_state.player_states[victim_seat].death_description = cause
    logger.warning("{} died by {}.".format(game_state.player_states[victim_seat].name, cause))
    return

def empty_mana_pool(game_state: GameState) -> None:
    for state in game_state.player_states:
        state.floating_mana = defaultdict(lambda: 0)

def pass_turn(game_state: GameState) -> None:
    # complete old turn
    game_state.halfturns_completed += 1
    next_active_seat: int = (game_state.active_player_index + 1) % len(game_state.player_states)
    game_state.active_player_index = next_active_seat

    # Handle setup of new turn
    logger.info("{} will draw a card for turn".format(game_state.player_states[next_active_seat].name))
    execute_action(next_active_seat, game_state, draw_card)
    game_state.upcoming_event = PlayerEvent.MAIN_PHASE_EMPTY_STACK

def get_player_position(info: PlayerState, game_state:GameState) -> int:
    return game_state.player_states.index(info)

##################################    
# Actions to be handled by proxy
##################################

def draw_card(acting_seat: int, game_state: GameState) -> None:
    hand: list[CardInstance] = game_state.player_states[acting_seat].cards_in_hand
    library: list[CardInstance] = game_state.player_states[acting_seat].cards_in_library
    # Decking is handled prior
    card_drawn: CardInstance = library.pop(0)
    hand.append(card_drawn)
    return
    
def deal_damage(acting_seat: int, game_state: GameState, target_seat:int, damage_amount:int) -> None:
    game_state.player_states[target_seat].current_life -= damage_amount
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
    and not game_state.player_states[acting_seat].cards_in_library:
        return replacement_catalog[const.DECKING].replacing_action(acting_seat, game_state, *args, **kwargs)
        
    return attempted_action(acting_seat, game_state, *args, **kwargs)
    
def execute_action(acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                    *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
    action_result: ActionResult = _execute_action_with_replacment(acting_seat, game_state, attempted_action, *args, **kwargs)
    check_state_based_actions(game_state)
    return action_result

