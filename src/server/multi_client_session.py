from server.player_connection import SessionSeat
from server.player_connection import PlayerController
from environment.base import BaseEnvironment
from environment.player import Player
from rendering.simple import SimpleVisualization

import time
from functools import reduce
from typing import Optional
import operator
from logging import Logger
from logging_config import main_log, player1_log, player2_log
import app_config as conf


class MultiClientSession:

    def __init__(self) -> None:
        alice: Player = Player("Alice")
        bob: Player = Player("Bob")
        self.env: BaseEnvironment = BaseEnvironment([alice, bob])
        self.seats: list[Optional[SessionSeat]] = [None, None]
        self.vis: SimpleVisualization = SimpleVisualization()    

    def connect(self) -> Optional[PlayerController]:
        main_log.info("Trying to seat a new agent at session")
        if self.seats[0] is None:
            return self.connect_to_seat(0)
        if self.seats[1] is None:
            return self.connect_to_seat(1)
        return
    
    def connect_to_seat(self, seat_position: int) -> Optional[PlayerController]:
        if seat_position >= len(self.seats):
            main_log.warning("Trying to connect to a seat index out of bounds!")
            return
        if self.seats[seat_position] is not None:
            main_log.warning("Trying to connect to an occupied seat")
            return
        player: Player = self.env.players[seat_position]
        player_log: Logger | None = None
        if seat_position == 0:
            player_log = player1_log
        if seat_position == 1:
            player_log = player2_log
        if player_log is None:
            return
        player_log.info("Seating new agent.")
        cont = PlayerController(player, player_log)
        self.seats[seat_position] = SessionSeat(self.env, cont)
        main_log.info("Seated agent at {} with new player {}". format(cont.player.name, seat_position))
        return cont
    
    def run_game(self) -> None:
        last_timestamp: float = time.time()
        delta_t: float = 0.0
        while not self.env.game_over:
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
                cont.reset_decision_info()
                cont.upcoming_decision = self.env.get_upcoming_decision()

            # Await Player Input
            while cont.intended_next_decision is None:
                delta_t = time.time() - last_timestamp
                time.sleep(max(conf.SESSION_TICK_LENGTH - delta_t, 0))
                last_timestamp = time.time()
                main_log.debug("GameTick: Waiting for Player Input from {}".format(cont.player.name))
            
            # Read Player Input
            with cont.lock:
                player_intent: str = cont.intended_next_decision

            # Update Screen without lock as it only depends on the environment
            self.env.step(self.env.get_active_player(), player_intent)
            self.vis.step(self.env)

        main_log.info("Game concluded. Shutting down session!")
        return
    
    def get_active_player_controller(self) -> Optional[PlayerController]:
        active_seat: Optional[SessionSeat] = self._get_active_seat()
        if active_seat is None:
            return None
        return active_seat.controller


    def _get_active_seat(self) -> Optional[SessionSeat]:
        if self.seats[0] is None or self.seats[1] is None:
            main_log.error("Can't get active seat because a player disconnected!")
            return
        for seat in self.seats:
            assert seat is not None
            if self.env.get_active_player() == seat.controller.player: 
                return seat
        main_log.error("Active Player {} does not belong to any connected seat!".format(self.env.get_active_player()))
        return

