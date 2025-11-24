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
        self.halfturns_completed: int = 0
        self.action_events_completed: int = 0
        self.active_player_index: int = 0
        self.game_over: bool = False
        self.players: list[Player] = players

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Completed Halfturns: {}".format(self.halfturns_completed),
            "Completed ActionEvents: {}".format(self.action_events_completed),
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
    
    def step(self, acting_player: Player, action_info: tuple[int, str]) -> ActionEvent:
        # Don't respond if the game is over
        if(self.game_over):
            return ActionEvent(const.GAMEOVER, [])
        
        # Handle action of step
        # TODO-1: How to handle exceptions/enforcement for nonsensical action inputs
        action_event_from_agent: ActionEvent = BaseEnvironment.action_event_catalog[action_info[0]]
        logger.info("Handling action {}:{} from {}".format(action_event_from_agent.name, action_info[1], acting_player.name))
        if ((action_event_from_agent.name == "Combat") and
            (action_info[1] in action_event_from_agent.possible_actions)):
            self.handle_combat_action(acting_player, action_info[1])

        # Update environment with step completion
        self.check_state_based_action()
        self.action_events_completed += 1
        if(self.action_events_completed >= len(BaseEnvironment.action_event_catalog)):
            self.pass_turn()
        return self.action_event_catalog[self.action_events_completed]
    
    def handle_combat_action(self, acting_player: Player, action: str) -> None:
        if(action==const.COMBAT_ATTACK):
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


    def pass_turn(self) -> None:
        self.halfturns_completed += 1
        self.action_events_completed = 0
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
