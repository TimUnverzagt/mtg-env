from environment.player import Player
from environment.action_event import ActionEvent
from operator import attrgetter as getter

class BaseEnvironment:
    action_event_catalog: list[ActionEvent] = [
        ActionEvent("MainPhase", ["Pass", "PlayCreature"]),
        ActionEvent("Combat", ["Pass", "AttackWithAll"])
    ]


    def __init__(self, players: list[Player]) -> None:
        print("Creating new base environment")
        self.halfturns_completed: int = 0
        self.action_events_completed: int = 0
        self.active_player_index: int = 0
        self.players: list[Player] = players

    def __str__(self) -> str:
        return "\n".join([
            "Active Player: Index [{}] | Name [{}]".format(self.active_player_index, self.players[self.active_player_index].name),
            "Completed Halfturns: {}".format(self.halfturns_completed),
            "Completed ActionEvents: {}".format(self.action_events_completed),
            "Players: {}".format(" | ".join(map(getter("name"), self.players)))
        ])
    
    def step(self, acting_player: Player, action_info: tuple[int, str]) -> ActionEvent:
        print(self)
        self.action_events_completed += 1
        if(self.action_events_completed >= len(BaseEnvironment.action_event_catalog)):
            self.pass_turn()
        return self.action_event_catalog[self.action_events_completed]
    
    def pass_turn(self) -> None:
        self.halfturns_completed += 1
        self.action_events_completed = 0
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
