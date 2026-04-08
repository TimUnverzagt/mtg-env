from server.session.player_connection import PlayerController
import gameengine.core as GameEngine
from gameengine.constants import Action
#from game.state import GameState
from gameengine.player import PlayerInfo
from rendering.simple import SimpleVisualization

import time
from functools import reduce
from typing import Optional
import operator
import app_config as conf
from copy import deepcopy

from logging_config import session_log as logger


class MultiClientSession():

    def __init__(self) -> None:
        self.game_state = GameEngine.get_initial_game_state()
        self.seats: list[Optional[PlayerController]] = [None, None]
        self.vis: SimpleVisualization | None = None
        if conf.HUMAN_RENDERING:
            self.vis = SimpleVisualization()
        self.shutting_down: bool = False

    def connect(self, name: str) -> PlayerController | None:
        logger.info("Trying to seat a new agent at session")
        if self.seats[0] is None:
            return self.connect_to_seat(0, name)
        if self.seats[1] is None:
            return self.connect_to_seat(1, name)
        return
    
    def connect_to_seat(self, seat_position: int, name: str) -> PlayerController | None:
        if seat_position >= len(self.seats):
            logger.error("Aborting connection: Tried to connect to a seat index out of bounds!")
            return
        if self.seats[seat_position] is not None:
            logger.error("Aborting connection: Tried to connect to an occupied seat")
            return
        player_info: PlayerInfo = self.game_state.player_infos[seat_position]
        cont = PlayerController(player_info, seat_position, name, deepcopy(self.game_state))
        self.seats[seat_position] = cont
        logger.info("Seated agent at seat {} with new player {}". format(seat_position, cont.player_info.name))
        return cont
    
    def tick_session(self) -> None:
        last_timestamp: float = time.time()
        delta_t: float = 0.0
        while not self.game_state.game_over:
            delta_t = time.time() - last_timestamp
            last_timestamp = time.time()
            if (delta_t < conf.SESSION_TICK_LENGTH):
                time.sleep(max(conf.SESSION_TICK_LENGTH - delta_t, 0))
            logger.debug("SessionTick: Running GameLoop")

            seats_filled: bool = reduce(operator.and_ ,map(lambda seat: seat is not None, self.seats), True)
            if not seats_filled: 
                logger.debug("Waiting for more players...")
                continue

            # Retrieve Player
            cont: Optional[PlayerController] = self.get_active_player_controller()
            if cont is None: 
                continue
            assert cont is not None
            
            # Prompt Player Input
            with cont.session_condition:
                logger.debug("SessionTick: {}: Prompting Player with state {}".format(
                    cont.player_info.name,
                    self.game_state
                    ))
                cont.upcoming_event = self.game_state.upcoming_event.value
                cont.game_state_before_action = self.game_state
                cont.session_condition.notify_all()

                # Await Player Input
                logger.debug("SessionTick: {}: Waiting for Player Input".format(cont.player_info.name))
                cont.session_condition.wait_for(cont.get_intent_predicate(expected_to_be_set=True))

                # Process Player Input and report state update
                assert cont.intended_next_decision is not None
                player_intent: Action = cont.intended_next_decision
                cont.intended_next_decision = None
                GameEngine.step(self.game_state.active_player_index, player_intent, self.game_state)
                cont.set_action_result(self.game_state)
                logger.debug("SessionTick: {}: Anwsering player with new state {}".format(
                    cont.player_info.name,
                    self.game_state
                    ))
                cont.session_condition.notify_all()


            if(conf.HUMAN_RENDERING):
                assert self.vis is not None
                self.vis.step(self.game_state)

        logger.info("Game concluded. Shutting down session!")

        self.shutting_down = True
        for cont in self.seats:
            assert cont is not None
            with cont.session_condition:
                cont.session_condition.notify_all()
        return


    def get_active_player_controller(self) -> Optional[PlayerController]:
        if self.seats[0] is None or self.seats[1] is None:
            logger.error("Can't get active controller because a player disconnected!")
            return
        
        active_player_info: PlayerInfo = self.game_state.player_infos[self.game_state.active_player_index] 
        for controller in self.seats:
            assert controller is not None
            if active_player_info == controller.player_info: 
                return controller
        logger.error("PlayerInfo does not align with any controller! This should never happen!!")
        return

