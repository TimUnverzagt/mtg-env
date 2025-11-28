from environment.player import Player
from environment.action_event import ActionEvent
import environment.constants as const

import logging
logger = logging.getLogger(__name__)



class BaseEnvironment:
    action_event_catalog: list[ActionEvent] = [
        ActionEvent(const.MAINPHASE, [const.MAINPHASE_PASS, const.MAINPHASE_PLAY_CREATURE]),
        ActionEvent(const.COMBAT, [const.COMBAT_PASS, const.COMBAT_ATTACK])        
    ]


    def __init__(self, players: list[Player]) -> None:
        logger.info("Creating new base environment")
        self.player_turns_completed: int = 0
        self.steps_in_turn_completed: int = 0
        self.active_player_index: int = 0
        self.game_over: bool = False
        self.players: list[Player] = players

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Completed Halfturns: {}".format(self.player_turns_completed),
            "Completed ActionEvents: {}".format(self.steps_in_turn_completed),
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
    
    def step(self, acting_player: Player, action_info: str) -> None:
        # Don't respond if the game is over
        if(self.game_over):
            return
        
        applicable_action: ActionEvent = self.get_upcoming_action()

        # Handle action of step
        # TODO: How to handle exceptions/enforcement for nonsensical action inputs
        logger.info("Handling intent {} for action {} from {}".format(action_info, applicable_action.name, acting_player.name))
        if ((applicable_action.name == "Combat") and
            (action_info[1] in applicable_action.possible_actions)):
            self.handle_combat_action(acting_player, action_info[1])

        # Update environment with step completion
        self.check_state_based_action()
        self.steps_in_turn_completed += 1
        if(self.steps_in_turn_completed >= len(BaseEnvironment.action_event_catalog)):
            self.pass_turn()
        return 
    
    def handle_combat_action(self, acting_player: Player, action: str) -> None:
        if(action==const.COMBAT_ATTACK):
            logger.warning("{} is attacking!".format(acting_player.name))
            # Just use the only other player as target
            defending_player: Player = self.players[(self.active_player_index + 1) % len(self.players)]
            # Just decrease health by flat amount for poc
            defending_player.current_life -= 1
        return
    
    def check_state_based_action(self) -> None:
        # Check for dead players
        losing_players: list[Player] = list(filter(lambda player: player.current_life <= 0, self.players))
        surviving_players: list[Player] = list(filter(lambda player: player not in losing_players, self.players))
        if len(surviving_players) <= 1:
            self.game_over = True
            logger.info("Game ended by death of player(s)")
        if len(surviving_players) == 1:
            logger.info("{} won by survival".format(surviving_players[0].name))
        return
    
    def get_active_player(self) -> Player:
        return self.players[self.active_player_index]
    
    def get_upcoming_action(self) -> ActionEvent:
        return self.action_event_catalog[self.steps_in_turn_completed]


    def pass_turn(self) -> None:
        self.player_turns_completed += 1
        self.steps_in_turn_completed = 0
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
