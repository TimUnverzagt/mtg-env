from server.player_connection import PlayerSocket
from server.player_connection import PlayerController
from environment.base import BaseEnvironment
from environment.player import Player


class MultiClientSession:

    def __init__(self) -> None:
        alice: Player = Player("Alice")
        bob: Player = Player("Bob")
        self.env: BaseEnvironment = BaseEnvironment([alice, bob])
        self.socket1: PlayerSocket | None = None
        self.socket2: PlayerSocket | None = None

    def connect_to_Session(self) -> PlayerController | None:
        if (self.socket1 is not None) and (self.socket2 is not None):
            return
        
        client_controller: PlayerController = PlayerController()
        if self.socket1 is None:
            self.socket1 = PlayerSocket("Alice", self.env, client_controller)
        elif self.socket2 is None:
            self.socket2 = PlayerSocket("Bob", self.env, client_controller)

        return client_controller