class BaseEnvironment:
    halfturns_completed: int
    active_player: str


    def __init__(self) -> None:
        print("Creating new base environment")
        self.halfturns_completed = 0
        self.active_player = "Player 1"

    def __str__(self) -> str:
        return "Active Player: {}\nCompleted halfturns: {}".format(self.active_player, self.halfturns_completed)