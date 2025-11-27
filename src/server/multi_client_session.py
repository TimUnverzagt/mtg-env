from server.player_connection import SessionSeat
from server.player_connection import PlayerController
from environment.base import BaseEnvironment
from environment.player import Player


class MultiClientSession:

    def __init__(self) -> None:
        alice: Player = Player("Alice")
        bob: Player = Player("Bob")
        self.env: BaseEnvironment = BaseEnvironment([alice, bob])
        self.seat1: SessionSeat | None = None
        self.seat2: SessionSeat | None = None

    def connect(self) -> PlayerController | None:
        if (self.seat1 is not None) and (self.seat2 is not None):
            return
        
        client_controller: PlayerController = PlayerController()
        if self.seat1 is None:
            self.seat1 = SessionSeat(self.env.players[0], self.env, client_controller)
        elif self.seat2 is None:
            self.seat2 = SessionSeat(self.env.players[1], self.env, client_controller)

        return client_controller
    
    def step_game(self) -> None:
        #TODO
        #active_player: Player = self.env.get_active_player()
        return
