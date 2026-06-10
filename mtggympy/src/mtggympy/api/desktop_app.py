from mtggympy.server.agents.external import ApiAgent
from mtggympy.server.session.multi_client_session import MultiClientSession as GameSession
from mtggympy.gui.rendering.glrender import GlRenderer

class DesktopApp():

    def __init__(self, session: GameSession, player_name: str) -> None:
        self.agent: ApiAgent = ApiAgent(session, player_name, target_seat=1)
        self.renderer: GlRenderer = GlRenderer()
    
    def run(self) -> None:
        return