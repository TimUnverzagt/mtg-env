from gameengine.player import PlayerInfo
from gameengine.priority.event import PlayerEvent
from gameengine.constants import ManaColor
from dataclasses import dataclass

@dataclass
class GameState:
    player_turns_completed: int
    steps_in_turn_completed: int
    active_player_index: int
    game_over: bool
    upcoming_event: PlayerEvent
    player_infos: list[PlayerInfo]
    winner_positions: list[int]
    floating_mana: dict[ManaColor, int]

    def __str__(self) -> str:
        return "\n".join([
            "---------------------------------------------",
            "---------------- Environment ----------------",
            "---------------------------------------------",
            "Active Player Index: {}".format(self.active_player_index),
            "Floating Mana: {}".format(self.floating_mana[ManaColor.COLORLESS]),
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
