from __future__ import annotations
from collections import defaultdict
from mtggympy.gameengine.constants import GameStep, ManaColor
import mtggympy.gameengine.constants as const
from mtggympy.gameengine.player import Player
from mtggympy.gameengine.priority.event import ActionIntent, PlayerEvent, ActionData
from mtggympy.gameengine.gameobjects import CardInstance, CreatureInstance, LandInstance
from mtggympy.gameengine.state import GameState, PlayerState, is_player_alive
from mtggympy.gameengine.cards.catalog.creatures import CreatureNames as CreatureNames
from mtggympy.gameengine.capabilities import ManaProvider
import mtggympy.gameengine.parsing as parse

from mtggympy.helpers.dict_operations import first_dict_can_fit_second_by_value
from typing import Callable, Generic, ParamSpec, TypeVar, Any, Concatenate

from mtggympy.logging_config import engine_log as logger


##################################    
# Steps
##################################
# Steps return whether they completed succesfully

def upkeep(game_state:GameState) -> bool:
    active_battlefield: list[CardInstance] = game_state.player_states[game_state.active_player_index].cards_in_play
    for card in active_battlefield:
        card.tapped = False
        if isinstance(card, CreatureInstance):
            card.summoning_sick = False
    return True

def draw_step(game_state:GameState) -> bool:
    # Handle setup of new turn
    if(game_state.halfturns_completed <= 0):
        logger.info("{} will skip their draw on the first turn".format(game_state.player_states[game_state.active_player_index].name))
        return True
    logger.info("{} will draw a card for turn".format(game_state.player_states[game_state.active_player_index].name))
    execute_action(game_state.active_player_index, game_state, draw_card)
    return True

def main_phase(acting_seat: int, intent: ActionIntent, game_state: GameState) -> bool:
    match intent.action:
        case ActionData.PASS:
            return True
        case ActionData.PLAY_CARD:
            target_card: CardInstance|None = parse.card_for_playing(acting_seat, intent, game_state)
            if target_card is None:
                return False
            return play_card(acting_seat, game_state, target_card)
        case ActionData.ACTIVATE_LANDS:
            target_lands: list[CardInstance] | None = parse.lands_for_activation(acting_seat, intent, game_state)
            if target_lands is None:
                return False
            return activate_lands(acting_seat, game_state, target_lands)
        case _:
            handle_illegal_action(intent.action, PlayerEvent.MAINPHASE_EMPTY_STACK)
            return False


def combat(acting_seat: int, intent: ActionIntent, game_state: GameState) -> bool:
    match intent.action:
        case ActionData.PASS:
            return True
        case ActionData.ATTACK:
            target_creatures: list[CreatureInstance] | None = parse.creatures_for_attacking(acting_seat, intent, game_state)
            if target_creatures is None:
                logger.warning("No creatures recognized from parsed input!")
                return False
            return attack(acting_seat, game_state, target_creatures)
        case _:
            handle_illegal_action(intent.action, PlayerEvent.DECLARE_ATTACKS)
            return False

def end_step(game_state: GameState) -> bool:
    active_hand: list[CardInstance] = game_state.player_states[game_state.active_player_index].cards_in_hand
    max_hand_size: int = 7
    if len(active_hand) > max_hand_size:
        logger.info("Discarding down to handsize of {} automatically".format(max_hand_size))
        cards_to_discard: list[CardInstance] = active_hand[max_hand_size:]
        logger.info("Discarding {} cards".format(len(cards_to_discard)))
        active_hand = active_hand[:7]        
    return True


##################################    
# Pure Tranistion after parsing
##################################
def activate_lands(acting_seat: int, game_state:GameState, target_lands: list[CardInstance]) -> bool:
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to activate lands. Refusing to process intent!")
        return False
    new_mana: list[ManaColor] = []
    for card in target_lands:
        if not isinstance(card, ManaProvider):
            logger.error("Target land {} is not a mana provider. Refusing to process intent!".format(card.card_name))
            return False
        if not card.is_ready():
            logger.error("Target land {} is not ready. Refusing to process intent!".format(card.card_name))
            return False
        new_mana += card.produce_mana()
    for color in new_mana:
        game_state.player_states[acting_seat].floating_mana[color] += 1
    return True

def play_card(acting_seat: int, game_state:GameState, card: CardInstance) -> bool:
    if game_state.active_player_index != acting_seat:
        logger.error("Non-active player is trying to play a card. Refusing to process intent!")
        return False
    player_state: PlayerState = game_state.player_states[acting_seat]
    hand: list[CardInstance] = player_state.cards_in_hand
    battlefield: list[CardInstance] = player_state.cards_in_play
    floating_mana: dict[ManaColor, int] = player_state.floating_mana

    if isinstance(card, CreatureInstance):
        assert card.mana_cost is not None
        if not first_dict_can_fit_second_by_value(floating_mana, card.mana_cost):
            logger.error("{} is trying to play {} without having enough mana. Refusing to process intent".format(
                player_state.name, card.card_name
            ))
            logger.debug("Available mana: {}".format(floating_mana)) 
            logger.debug("Required mana: {}".format(card.mana_cost))
            logger.debug("Cards in hand: {}".format(list(map(lambda card: card.card_name, hand))))
            return False
        for color in card.mana_cost:
            floating_mana[color] -= card.mana_cost[color]
        card.summoning_sick = True
    if isinstance(card, LandInstance):
        if game_state.lands_played_this_turn >= 1:
            logger.error("{} is trying to play with {} prior land drops. Refusing to process intent".format(
                player_state.name, game_state.lands_played_this_turn
            ))
            return False
        game_state.lands_played_this_turn += 1        
    hand.remove(card)
    battlefield.append(card)
    return True

def attack(acting_seat: int, game_state: GameState, target_creatures: list[CreatureInstance]) -> bool:
    logger.warning("Turn {}/{}: {} is attacking!".format(
        game_state.halfturns_completed,
        len(game_state.player_states),
        game_state.player_states[acting_seat].name)
    )
    total_damage: int = 0
    for creature in target_creatures:
        if creature.tapped:
            logger.error("Target creature {} is tapped and can not attack. Refusing to process intent!".format(creature.card_name))
            return False
        if creature.summoning_sick:
            logger.error("Target creature {} is summoning sick and can not attack. Refusing to process intent!".format(creature.card_name))
            return False
        creature.tapped = True
        total_damage += creature.power
    defending_position: int =(game_state.active_player_index + 1) % len(game_state.player_states)#
    return execute_action(acting_seat, game_state, deal_damage, defending_position, total_damage)

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
    
def deal_damage(acting_seat: int, game_state: GameState, target_seat:int, damage_amount:int) -> bool:
    game_state.player_states[target_seat].current_life -= damage_amount
    return True


##################################
# Misc
##################################
def get_initial_game_state() -> GameState:
    player1: Player = Player("Player1")
    player2: Player = Player("Player2")
    game_state: GameState = GameState(
        halfturns_completed = 0,
        active_player_index = 0,
        game_over = False,
        step=GameStep.UPKEEP,
        player_states = [player1.info, player2.info],
        winner_positions=[],
        lands_played_this_turn=0
    )
    return game_state

def pass_turn(game_state: GameState) -> bool:
    game_state.halfturns_completed += 1
    next_active_seat: int = (game_state.active_player_index + 1) % len(game_state.player_states)
    game_state.active_player_index = next_active_seat
    game_state.lands_played_this_turn = 0
    return True

def get_player_position(info: PlayerState, game_state:GameState) -> int:
    return game_state.player_states.index(info)

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

def empty_mana_pools(game_state: GameState) -> None:
    for state in game_state.player_states:
        state.floating_mana = defaultdict(lambda: 0)


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

