from game.player import PlayerInfo

from dataclasses import dataclass

@dataclass
class GameState:
    player_turns_completed: int
    steps_in_turn_completed: int
    active_player_index: int
    game_over: bool
    player_infos: list[PlayerInfo]
