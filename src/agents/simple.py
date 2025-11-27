from server.multi_client_session import MultiClientSession as GameSession
from server.player_connection import PlayerController

class Goldfish:
    def __init__(self, session: GameSession):
        self.session: GameSession = session
        self.controller: PlayerController | None = session.connect()


