from environment.player import Player
from operator import attrgetter as getter

class BaseEnvironment:
    halfturns_completed: int
    active_player_index: int
    players: list[Player]


    def __init__(self) -> None:
        print("Creating new base environment")
        self.halfturns_completed = 0
        self.active_player_index = 0
        self.players = [Player("Alice"), Player("Bob")]

    def __str__(self) -> str:
        return "\n".join([
            "Active Player: Index [{}] | Name [{}]".format(self.active_player_index, self.players[self.active_player_index].name),
            "Completed halfturns: {}".format(self.halfturns_completed),
            "Players: {}".format(" | ".join(map(getter("name"), self.players)))
        ])
    
    def pass_turn(self) -> None:
        self.halfturns_completed += 1
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
