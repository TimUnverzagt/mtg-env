import game.constants as const
from game.player import PlayerInfo, is_player_alive
from game.decision_event import DecisionEvent
from game.action_replacement import ActionProxy
from game.card import Card
from game.state import GameState

from package.logging_config import env_log

action_proxy: ActionProxy = ActionProxy()

def step(acting_seat: int, decision_intent: str, game_state: GameState) -> None:
    # Don't respond if the game is over
    if(game_state.game_over):
        return
        
    acting_player_info: PlayerInfo = game_state.player_infos[acting_seat]
    applicable_decision: DecisionEvent = get_upcoming_decision(game_state)

    # Handle decision of step
    # TODO: How to handle exceptions/enforcement for nonsensical decision inputs
    env_log.info("Handling intent '{}' for decision event '{}' from {}".format(
        decision_intent, applicable_decision.name, acting_player_info.name
        ))
    if ((applicable_decision.name == const.COMBAT)):
        handle_combat_decision(acting_seat, decision_intent, game_state)
    # Stop immediatly if game is over now
    if(game_state.game_over):
        return
        
    game_state.steps_in_turn_completed += 1
    if(game_state.steps_in_turn_completed >= len(const.DECISION_EVENT_CATALOG)):
        pass_turn(game_state)
    return 


def handle_combat_decision(acting_seat: int, decision: str, game_state: GameState) -> None:
    if(decision==const.COMBAT_ATTACK):
        env_log.warning("{} is attacking!".format(game_state.player_infos[acting_seat].name))
        # Just use the only other player as target
        defending_position: int =(game_state.active_player_index + 1) % len(game_state.player_infos)
        # Just decrease health by flat amount for poc
        action_proxy.execute_action(acting_seat, game_state, deal_damage, defending_position, 1)
    return

def update_game_state(game_state: GameState) -> None:
    env_log.debug("Updating Game State")
    # Check for dying players
    alive_player_infos: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_infos))
    players_dying_from_hp: list[PlayerInfo] = list(filter(lambda player_info: player_info.current_life <= 0, alive_player_infos))
    if len(players_dying_from_hp) > 0:
        for player_info in players_dying_from_hp:
            handle_player_death(get_player_position(player_info, game_state), game_state, "having 0 or less life");
        
    check_for_game_end(game_state)
    return

def check_for_game_end(game_state: GameState):
    surviving_players: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), game_state.player_infos))
    if len(surviving_players) <= 1:
        game_state.game_over = True
        env_log.info("Game ended by death of player(s)")
    if len(surviving_players) == 1:
        env_log.info("{} won by survival".format(surviving_players[0].name))

def kill_player_by_decking(victim_seat: int, game_state: GameState) -> None:
    handle_player_death(victim_seat, game_state, "drawing from an empty library")
    return
    
def handle_player_death(victim_seat: int, game_state: GameState, cause: str):
    game_state.player_infos[victim_seat].death_description = cause
    env_log.warning("{} died by {}.".format(game_state.player_infos[victim_seat].name, cause))
    return
    
def get_upcoming_decision(game_state: GameState) -> DecisionEvent:
    return const.DECISION_EVENT_CATALOG[game_state.steps_in_turn_completed]

def pass_turn(game_state: GameState) -> None:
    # complete old turn
    game_state.player_turns_completed += 1
    game_state.steps_in_turn_completed = 0
    next_active_seat: int = (game_state.active_player_index + 1) % len(game_state.player_infos)
    game_state.active_player_index = next_active_seat

    # Handle setup of new turn
    env_log.info("{} will draw a card for turn".format(game_state.player_infos[next_active_seat].name))
    action_proxy.execute_action(next_active_seat, game_state, draw_card)

def get_player_position(info: PlayerInfo, game_state:GameState) -> int:
    return game_state.player_infos.index(info)

##################################    
# Actions to be handled by proxy
##################################

def draw_card(acting_seat: int, game_state: GameState) -> None:
    game_state.player_infos[acting_seat].cards_in_hand.append(Card(3))
    # Decking is handled prior
    game_state.player_infos[acting_seat].cards_in_library -= 1
    return
    
def deal_damage(acting_seat: int, game_state: GameState, target_seat:int, damage_amount:int) -> None:
    game_state.player_infos[target_seat].current_life -= damage_amount
    return    
