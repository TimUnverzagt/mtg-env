from environment.player import Player
from operator import attrgetter as getter

class BaseEnvironment:


    def __init__(self) -> None:
        print("Creating new base environment")
        self.halfturns_completed: int = 0
        self.active_player_index: int = 0
        self.players: list[Player] = [Player("Alice"), Player("Bob")]

    def __str__(self) -> str:
        return "\n".join([
            "Active Player: Index [{}] | Name [{}]".format(self.active_player_index, self.players[self.active_player_index].name),
            "Completed halfturns: {}".format(self.halfturns_completed),
            "Players: {}".format(" | ".join(map(getter("name"), self.players)))
        ])
    
    def pass_turn(self) -> None:
        self.halfturns_completed += 1
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
