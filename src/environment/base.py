import environment.constants as const
from environment.player import Player
from environment.decision_event import DecisionEvent
from environment.action_replacement import ActionProxy
from environment.card import Card

from logging_config import env_log



class BaseEnvironment:
    decision_event_catalog: list[DecisionEvent] = [
        DecisionEvent(const.MAINPHASE, 0, [const.MAINPHASE_PASS, const.MAINPHASE_PLAY_CREATURE]),
        DecisionEvent(const.COMBAT, 0,[const.COMBAT_PASS, const.COMBAT_ATTACK])        
    ]


    def __init__(self, players: list[Player]) -> None:
        env_log.info("Creating new base environment")
        self.player_turns_completed: int = 0
        self.steps_in_turn_completed: int = 0
        self.active_player_index: int = 0
        self.game_over: bool = False
        self.players: list[Player] = players
        self.action_proxy: ActionProxy = ActionProxy(self)

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Completed Halfturns: {}".format(self.player_turns_completed),
            "Completed DecisionEvents: {}".format(self.steps_in_turn_completed),
            "Active Player Index: {}".format(self.active_player_index),
            "Game over: {}".format(self.game_over),
            "---------------------------------------------",
            "Player 0:",
            str(self.players[0]),
            "---------------------------------------------",
            "Player 1:",
            str(self.players[1]),
            "---------------------------------------------"
        ])
    
    def step(self, acting_player: Player, decision_intent: str) -> None:
        # Don't respond if the game is over
        if(self.game_over):
            return
        
        applicable_decision: DecisionEvent = self.get_upcoming_decision()

        # Handle decision of step
        # TODO: How to handle exceptions/enforcement for nonsensical decision inputs
        env_log.info("Handling intent '{}' for decision event '{}' from {}".format(
            decision_intent, applicable_decision.name, acting_player.name
            ))
        if ((applicable_decision.name == const.COMBAT)):
            self.handle_combat_decision(acting_player, decision_intent)
        # Stop immediatly if game is over now
        if(self.game_over):
            return
        
        self.steps_in_turn_completed += 1
        if(self.steps_in_turn_completed >= len(BaseEnvironment.decision_event_catalog)):
            self.pass_turn()
        return 
    
    def handle_combat_decision(self, acting_player: Player, decision: str) -> None:
        if(decision==const.COMBAT_ATTACK):
            env_log.warning("{} is attacking!".format(acting_player.name))
            # Just use the only other player as target
            defending_player: Player = self.players[(self.active_player_index + 1) % len(self.players)]
            # Just decrease health by flat amount for poc
            self.action_proxy.execute_action(acting_player, self.deal_damage, defending_player, 1)
        return
    
    def update_game_state(self) -> None:
        env_log.debug("Updating Game State")
        # Check for dying players
        alive_players: list[Player] = list(filter(lambda player: player.is_alive(), self.players))
        players_dying_from_hp: list[Player] = list(filter(lambda player: player.current_life <= 0, alive_players))
        if len(players_dying_from_hp) > 0:
            for player in players_dying_from_hp:
                self.handle_player_death(player, "having 0 or less life");
        
        self.check_for_game_end()
        return
    
    def check_for_game_end(self):
        surviving_players: list[Player] = list(filter(lambda player: player.is_alive(), self.players))
        if len(surviving_players) <= 1:
            self.game_over = True
            env_log.info("Game ended by death of player(s)")
        if len(surviving_players) == 1:
            env_log.info("{} won by survival".format(surviving_players[0].name))
    
    def kill_player_by_decking(self, actor: Player) -> None:
        self.handle_player_death(actor, "drawing from an empty library")
        return
    
    def handle_player_death(self, victim: Player, cause: str):
        victim.death_description = cause
        env_log.info("{} died by {}.".format(victim.name, cause))
        return

    def get_active_player(self) -> Player:
        return self.players[self.active_player_index]
    
    def get_upcoming_decision(self) -> DecisionEvent:
        return self.decision_event_catalog[self.steps_in_turn_completed]


    def pass_turn(self) -> None:
        # complete old turn
        self.player_turns_completed += 1
        self.steps_in_turn_completed = 0
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

        # Handle setup of new turn
        next_player: Player =  self.get_active_player()
        env_log.info("{} will draw a card for turn".format(next_player.name))
        self.action_proxy.execute_action(next_player, self.draw_card)

    
    # Action to be handled by proxy

    def draw_card(self, actor: Player) -> None:
        actor.cards_in_hand.append(Card(3))
        # Decking is handled prior
        actor.cards_in_library -= 1
        return
    
    def deal_damage(self, actor:Player, target:Player, damage_amount:int) -> None:
        target.current_life -= damage_amount
        return
