import copy
from threading import Thread, Condition

from mtggympy.helpers.predicate_extensions import build_joint_predicate
from mtggympy.logging_config import desktop_app_log as logger

from mtggympy.server.agents.console import ConsoleAgent
#from mtggympy.server.session.player_connection import PlayerController
from mtggympy.server.session.multi_client_session import MultiClientSession as GameSession
from mtggympy.gui.rendering.glrender import GlRenderer
from mtggympy.server.session.player_connection import PlayerController

class DesktopApp():

    def __init__(self, session: GameSession, player_name: str) -> None:
        self.agent: ConsoleAgent = ConsoleAgent(session, player_name, target_seat=0, wait_for_state_reading=True)
        self.renderer: GlRenderer = GlRenderer()
        self.agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)
        self.game_thread: Thread = Thread(target=self.run, daemon=True)
    

    def start(self):
        logger.debug("Starting Threads")
        self.agent_thread.start()
        self.game_thread.start()

    def run(self) -> None:
        Condition().wait_for(lambda: self.agent.controller is not None)
        while not self.agent.session.shutting_down:
            assert self.agent.controller is not None
            cont: PlayerController = self.agent.controller
            with cont.state_reading_condition:
                logger.debug("Waiting for game state prior to agent action.")
                cont.state_reading_condition.wait_for(build_joint_predicate(
                    cont.get_ready_for_session_consumption_predicate(),
                    cont.get_last_state_read_predicate(False)))
                with self.renderer.obs_condition:
                    self.renderer.observations = copy.deepcopy(self.agent.controller.game_state_before_action)
                    cont.last_state_successfully_read = True
                    cont.state_reading_condition.notify_all()
                logger.debug("Waiting for game state after agent action.")
                cont.state_reading_condition.wait_for(self.agent.controller.get_last_state_read_predicate(False))
                with self.renderer.obs_condition:
                    self.renderer.observations = copy.deepcopy(self.agent.controller.game_state_after_action)
                    cont.last_state_successfully_read = True
                    cont.state_reading_condition.notify_all()
