import game.constants as const
from game.player import PlayerInfo, is_player_alive
from game.decision_event import DecisionEvent
from game.action_replacement import ActionProxy
from game.card import Card
from game.state import GameState

from package.logging_config import env_log

class GameEngine:


    def __init__(self, player_infos: list[PlayerInfo]) -> None:
        env_log.info("Creating new base environment")
        self.game_state: GameState = GameState(
            player_turns_completed = 0,
            steps_in_turn_completed = 0,
            active_player_index = 0,
            game_over = False,
            player_infos = player_infos
        )
        self.action_proxy: ActionProxy = ActionProxy(self)

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Completed Halfturns: {}".format(self.game_state.player_turns_completed),
            "Completed DecisionEvents: {}".format(self.game_state.steps_in_turn_completed),
            "Active Player Index: {}".format(self.game_state.active_player_index),
            "Game over: {}".format(self.game_state.game_over),
            "---------------------------------------------",
            "Player 0:",
            str(self.game_state.player_infos[0]),
            "---------------------------------------------",
            "Player 1:",
            str(self.game_state.player_infos[1]),
            "---------------------------------------------"
        ])
        
    def step(self, acting_seat: int, decision_intent: str) -> None:
        # Don't respond if the game is over
        if(self.game_over):
            return
        
        acting_player_info: PlayerInfo = self.game_state.player_infos[acting_seat]
        applicable_decision: DecisionEvent = self.get_upcoming_decision()

        # Handle decision of step
        # TODO: How to handle exceptions/enforcement for nonsensical decision inputs
        env_log.info("Handling intent '{}' for decision event '{}' from {}".format(
            decision_intent, applicable_decision.name, acting_player_info.name
            ))
        if ((applicable_decision.name == const.COMBAT)):
            self.handle_combat_decision(acting_seat, decision_intent)
        # Stop immediatly if game is over now
        if(self.game_over):
            return
        
        self.game_state.steps_in_turn_completed += 1
        if(self.game_state.steps_in_turn_completed >= len(const.DECISION_EVENT_CATALOG)):
            self.pass_turn()
        return 
    
    def handle_combat_decision(self, acting_seat: int, decision: str) -> None:
        if(decision==const.COMBAT_ATTACK):
            env_log.warning("{} is attacking!".format(self.game_state.player_infos[acting_seat].name))
            # Just use the only other player as target
            defending_position: int =(self.game_state.active_player_index + 1) % len(self.game_state.player_infos)
            # Just decrease health by flat amount for poc
            self.action_proxy.execute_action(acting_seat, self.game_state, self.deal_damage, defending_position, 1)
        return
    
    def update_game_state(self) -> None:
        env_log.debug("Updating Game State")
        # Check for dying players
        alive_player_infos: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), self.game_state.player_infos))
        players_dying_from_hp: list[PlayerInfo] = list(filter(lambda player_info: player_info.current_life <= 0, alive_player_infos))
        if len(players_dying_from_hp) > 0:
            for player_info in players_dying_from_hp:
                self.handle_player_death(self._get_player_position(player_info), self.game_state, "having 0 or less life");
        
        self.check_for_game_end()
        return
    
    def check_for_game_end(self):
        surviving_players: list[PlayerInfo] = list(filter(lambda player_info: is_player_alive(player_info), self.game_state.player_infos))
        if len(surviving_players) <= 1:
            self.game_over = True
            env_log.info("Game ended by death of player(s)")
        if len(surviving_players) == 1:
            env_log.info("{} won by survival".format(surviving_players[0].name))
    
    def kill_player_by_decking(self, victim_seat: int, game_state: GameState) -> None:
        self.handle_player_death(victim_seat, game_state, "drawing from an empty library")
        return
    
    def handle_player_death(self, victim_seat: int, game_state: GameState, cause: str):
        game_state.player_infos[victim_seat].death_description = cause
        env_log.warning("{} died by {}.".format(game_state.player_infos[victim_seat].name, cause))
        return
    
    def get_upcoming_decision(self) -> DecisionEvent:
        return const.DECISION_EVENT_CATALOG[self.game_state.steps_in_turn_completed]


    def pass_turn(self) -> None:
        # complete old turn
        self.game_state.player_turns_completed += 1
        self.game_state.steps_in_turn_completed = 0
        next_active_seat: int = (self.game_state.active_player_index + 1) % len(self.game_state.player_infos)
        self.game_state.active_player_index = next_active_seat

        # Handle setup of new turn
        env_log.info("{} will draw a card for turn".format(self.game_state.player_infos[next_active_seat].name))
        self.action_proxy.execute_action(next_active_seat, self.game_state, self.draw_card)

    def _get_player_position(self, info: PlayerInfo) -> int:
        return self.game_state.player_infos.index(info)
        

    # Action to be handled by proxy

    def draw_card(self, acting_seat: int, game_state: GameState) -> None:
        game_state.player_infos[acting_seat].cards_in_hand.append(Card(3))
        # Decking is handled prior
        game_state.player_infos[acting_seat].cards_in_library -= 1
        return
    
    def deal_damage(self, acting_seat: int, game_state: GameState, target_seat:int, damage_amount:int) -> None:
        game_state.player_infos[target_seat].current_life -= damage_amount
        return
