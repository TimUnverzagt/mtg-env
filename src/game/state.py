from game.player import PlayerInfo

from dataclasses import dataclass

@dataclass
class GameState:
    player_turns_completed: int
    steps_in_turn_completed: int
    active_player_index: int
    game_over: bool
    player_infos: list[PlayerInfo]  

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
            str(self.player_infos[0]),
            "---------------------------------------------",
            "Player 1:",
            str(self.player_infos[1]),
            "---------------------------------------------"
        ])
