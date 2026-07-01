from abc import ABC, abstractmethod
from logging import Logger
from threading import Condition
from mtggympy.server.session.multi_client import MultiClientSession as GameSession
from mtggympy.gameengine.state.event import ActionIntent
from mtggympy.server.session.observed_state import ObservedGameState
from mtggympy.server.session.player_controller import PlayerController
from mtggympy.helpers.predicate_extensions import build_either_predicate

import time
import mtggympy.config.app_config as conf

class AgentBase(ABC):

    def __init__(self, session: GameSession, name: str, target_seat: int | None =  None, wait_for_state_processing: bool = False) -> None:
        self.session: GameSession = session
        self.needs_state_processing_time: bool = wait_for_state_processing
        maybe_controller: PlayerController | None
        if target_seat is None:
            maybe_controller = session.connect(name)
        else:
            maybe_controller = session.connect_to_seat(target_seat, name)
        assert maybe_controller is not None
        self.controller: PlayerController = maybe_controller

        # Shared variables
        self.state_processing_condition: Condition = Condition()
        self.state_to_process: ObservedGameState | None = None

    def play_game(self) -> None:
        cont: PlayerController = self.controller
        last_timestamp: float = time.time()
        delta_t: float = 0.0
        while not self.session.shutting_down:
            delta_t = time.time() - last_timestamp
            last_timestamp = time.time()
            if (delta_t < conf.AGENT_TICK_LENGTH):
                time.sleep(max(conf.AGENT_TICK_LENGTH - delta_t, 0))
            with cont.obs_before_action_condition:
                # Prior State
                cont.logger.debug("{}: Waiting for my turn to act. (Signaled by session setting prior_state)".format(cont.player_info.name))
                cont.obs_before_action_condition.wait_for(build_either_predicate(
                    lambda: cont.obs_before_action is not None,
                    lambda: self.session.shutting_down))
                if self.session.shutting_down:
                    return
                assert cont.obs_before_action
                prior_state: ObservedGameState = cont.obs_before_action
                self.process_prior_state(prior_state, cont.logger)
                cont.obs_before_action = None
                cont.obs_before_action_condition.notify_all()
                
            # Intent
            cont.logger.info("{}: Thinking on next event '{}'.".format(cont.player_info.name, prior_state.event.name))
            intent: ActionIntent = self.decide_on_action(prior_state, cont.logger)
            cont.logger.info("{}: Decided on action '{}'.".format(cont.player_info.name, cont.intent))
            with cont.intent_condition:
                cont.intent = intent
                cont.logger.info("{}: Set intent in controller".format(cont.player_info.name))
                cont.intent_condition.notify_all()
                cont.intent_condition.wait_for(lambda: cont.intent is None)

            with cont.obs_after_action_condition:
                # Posterior State              
                cont.logger.debug("{}: Waiting for response from game session.".format(cont.player_info.name))
                cont.obs_after_action_condition.wait_for(lambda: cont.obs_after_action is not None)
                assert cont.obs_after_action
                posteriori_state: ObservedGameState = cont.obs_after_action
                self.process_posteriori_state(posteriori_state, cont.logger)
                cont.obs_after_action = None
                cont.obs_after_action_condition.notify_all()

        cont.logger.info("Stopping because session is shutting down")
        self.shutdown()

    def process_posteriori_state(self, state: ObservedGameState, logger: Logger) -> None:
        if(self.needs_state_processing_time):
            with self.state_processing_condition:
                self.state_to_process = state
                self.state_processing_condition.notify_all()
                logger.debug("{}: Waiting for my game state to be processed before continuing".format(state.self_state.name))
                self.state_processing_condition.wait_for(lambda: self.state_to_process is None)
                self.state_processing_condition.notify_all()
        pass

    def process_prior_state(self, state: ObservedGameState, logger: Logger) -> None:
        if(self.needs_state_processing_time):
            with self.state_processing_condition:
                self.state_to_process = state
                self.state_processing_condition.notify_all()
                logger.debug("{}: Waiting for my game state to be processed before continuing".format(state.self_state.name))
                self.state_processing_condition.wait_for(lambda: self.state_to_process is None)
                self.state_processing_condition.notify_all()
        pass

    @abstractmethod
    def decide_on_action(self, state: ObservedGameState, logger: Logger) -> ActionIntent:
        pass

    def shutdown(self) -> None:
        pass