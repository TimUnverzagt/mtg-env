import copy
from threading import Thread, Condition

from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.helpers.predicate_extensions import build_either_predicate
from mtggympy.logging_config import desktop_ui_log as ui_logger
from mtggympy.logging_config import desktop_api_log as api_logger

from mtggympy.server.agents.console import ConsoleAgent
from mtggympy.server.agents.external import ApiAgent
#from mtggympy.server.session.player_connection import PlayerController
from mtggympy.server.session.multi_client import MultiClientSession as GameSession
from mtggympy.server.session.observed_state import ObservedGameState

from mtggympy.api.gui.rendering.opengl import GlRenderer
from mtggympy.helpers.pubsub import DESKTOP_INTENT_QUEUE


class DesktopApp():

    def __init__(self, session: GameSession, player_name: str, take_input_from_gui: bool = False) -> None:
        self.renderer: GlRenderer = GlRenderer()
        self.agent: ConsoleAgent | ApiAgent
        self.game_session: GameSession = session
        self.take_input_from_gui: bool = take_input_from_gui
        if take_input_from_gui:
            self.agent =ApiAgent(session, player_name, target_seat=0, wait_for_state_reading=True)
            self.ui_thread: Thread = Thread(target=self.run_ui_with_api, daemon=True)
        else:
            self.agent = ConsoleAgent(session, player_name, target_seat=0, wait_for_state_reading=True)
            self.ui_thread: Thread = Thread(target=self.run_ui_simple, daemon=True)
        self.agent_thread: Thread = Thread(target=self.agent.play_game, daemon=True)

        # Shared Variables
        self.ui_processing_state_condition: Condition = Condition()
        self.ui_state_to_process: ObservedGameState | None = None
    

    def start(self):
        self.agent_thread.start()
        self.ui_thread.start()
        if self.take_input_from_gui:
            self.run_api()

    def run_ui_simple(self) -> None:
        while not self.agent.session.shutting_down:
            with self.agent.state_processing_condition:
                ui_logger.debug("Waiting for game state")
                self.agent.state_processing_condition.wait_for(lambda: self.agent.state_to_process is not None)
                assert self.agent.state_to_process
                with self.renderer.obs_condition:
                    self.renderer.observations = copy.deepcopy(self.agent.state_to_process)
                ui_logger.debug("Forwarded game state")
                self.agent.state_to_process = None
                self.agent.state_processing_condition.notify_all()

    def run_ui_with_api(self) -> None:
        while not self.agent.session.shutting_down:
            with self.ui_processing_state_condition:
                ui_logger.debug("Waiting for game state")
                self.ui_processing_state_condition.wait_for(lambda: self.ui_state_to_process is not None)
                assert self.ui_state_to_process
                with self.renderer.obs_condition:
                    self.renderer.observations = copy.deepcopy(self.ui_state_to_process)
                ui_logger.debug("Forwarded game state")
                self.ui_state_to_process = None
                self.ui_processing_state_condition.notify_all()

    def run_api(self) -> None:
        api_logger.debug("Starting Api Thread")
        assert isinstance(self.agent, ApiAgent)
        api_agent: ApiAgent = self.agent
        while not api_agent.session.shutting_down:
            with api_agent.api_prior_state_processing_condition:
                api_logger.debug("Waiting for prior state to be set")
                api_agent.api_prior_state_processing_condition.wait_for(build_either_predicate(   
                    lambda: self.game_session.shutting_down,
                    lambda: api_agent.api_prior_state is not None  
                ))       
                if self.game_session.shutting_down:
                    api_logger.info("Game ended between steps!")
                    return             
                assert api_agent.api_prior_state
                prior_state: ObservedGameState = api_agent.api_prior_state
                api_logger.debug("Current Upcoming Event: {}".format(prior_state.event))
                with self.ui_processing_state_condition:
                    api_logger.debug("Sharing prior state with api")
                    self.ui_state_to_process = prior_state
                    self.ui_processing_state_condition.notify_all()
                    self.ui_processing_state_condition.wait_for(lambda: self.ui_state_to_process is None)
                api_agent.api_prior_state = None
                api_agent.api_prior_state_processing_condition.notify_all()
            
            api_logger.debug("Trying to access intent queue with {} element(s)".format(DESKTOP_INTENT_QUEUE.qsize()))
            intent: ActionIntent = DESKTOP_INTENT_QUEUE.get()
            api_logger.debug("Got {} from intent queue with args: {}".format(intent.action.name, intent.parameters))

            with api_agent.api_intent_condition:
                api_logger.debug("Declaring decision intent from external action")
                api_agent.api_intent = intent
                api_agent.api_intent_condition.notify_all()

            with api_agent.api_posteriori_state_processing_condition:
                api_logger.debug("waiting for response from agent")
                api_agent.api_posteriori_state_processing_condition.wait_for(lambda: api_agent.api_posteriori_state is not None)
                assert api_agent.api_posteriori_state
                api_logger.debug("Received processing confirmation via update of game state in controller")
                posteriori_state = api_agent.api_posteriori_state
                with self.ui_processing_state_condition:
                    api_logger.debug("Sharing postriori state with api")
                    self.ui_state_to_process = posteriori_state
                    self.ui_processing_state_condition.notify_all()
                    self.ui_processing_state_condition.wait_for(lambda: self.ui_state_to_process is None)
                
                api_agent.api_posteriori_state = None
                api_agent.api_posteriori_state_processing_condition.notify_all()

        if self.game_session.shutting_down:
            api_logger.info("Game is over ==> Shutting down")
            return

