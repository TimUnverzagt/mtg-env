from server.player_connection import PlayerController
import game.engine as GameEngine
#from game.state import GameState
from game.player import PlayerInfo
from rendering.simple import SimpleVisualization

import time
from functools import reduce
from typing import Optional
import operator
from logging_config import main_log
import app_config as conf
from copy import deepcopy


class MultiClientSession():

    def __init__(self) -> None:
        self.game_state = GameEngine.get_initial_game_state()
        self.seats: list[Optional[PlayerController]] = [None, None]
        self.vis: SimpleVisualization = SimpleVisualization()    

    def connect(self, name: str) -> PlayerController | None:
        main_log.info("Trying to seat a new agent at session")
        if self.seats[0] is None:
            return self.connect_to_seat(0, name)
        if self.seats[1] is None:
            return self.connect_to_seat(1, name)
        return
    
    def connect_to_seat(self, seat_position: int, name: str) -> PlayerController | None:
        if seat_position >= len(self.seats):
            main_log.error("Aborting connection: Tried to connect to a seat index out of bounds!")
            return
        if self.seats[seat_position] is not None:
            main_log.error("Aborting connection: Tried to connect to an occupied seat")
            return
        player_info: PlayerInfo = self.game_state.player_infos[seat_position]
        cont = PlayerController(player_info, seat_position, name, deepcopy(self.game_state))
        self.seats[seat_position] = cont
        main_log.info("Seated agent at seat {} with new player {}". format(seat_position, cont.player_info.name))
        return cont
    
    def run_game(self) -> None:
        last_timestamp: float = time.time()
        delta_t: float = 0.0
        while not self.game_state.game_over:
            delta_t = time.time() - last_timestamp
            last_timestamp = time.time()
            if (delta_t < conf.SESSION_TICK_LENGTH):
                time.sleep(max(conf.SESSION_TICK_LENGTH - delta_t, 0))
            main_log.debug("GameTick: Running GameLoop")

            seats_filled: bool = reduce(operator.and_ ,map(lambda seat: seat is not None, self.seats), True)
            if not seats_filled: 
                main_log.debug("Waiting for more players...")
                continue

            # Retrieve Player Intent
            cont: Optional[PlayerController] = self.get_active_player_controller()
            if cont is None: 
                continue
            assert cont is not None
            
            # Prompt Player Input
            with cont.lock:
                cont.upcoming_decision = GameEngine.get_upcoming_decision(self.game_state)

            # Await Player Input
            while cont.intended_next_decision is None:
                delta_t = time.time() - last_timestamp
                time.sleep(max(conf.SESSION_TICK_LENGTH - delta_t, 0))
                last_timestamp = time.time()
                main_log.debug("GameTick: Waiting for Player Input from {}".format(cont.player_info.name))
            
            # Process Player Input
            with cont.lock:
                player_intent: str = cont.intended_next_decision
                GameEngine.step(self.game_state.active_player_index, player_intent, self.game_state)
                cont.set_action_result(self.game_state)

            self.vis.step(self.game_state)

        main_log.info("Game concluded. Shutting down session!")
        return


    def get_active_player_controller(self) -> Optional[PlayerController]:
        if self.seats[0] is None or self.seats[1] is None:
            main_log.error("Can't get active controller because a player disconnected!")
            return
        
        active_player_info: PlayerInfo = self.game_state.player_infos[self.game_state.active_player_index] 
        for controller in self.seats:
            assert controller is not None
            if active_player_info == controller.player_info: 
                return controller
        main_log.error("PlayerInfo does not align with any controller! This should never happen!!")
        return

