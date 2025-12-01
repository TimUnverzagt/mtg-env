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


class MultiClientSession:

    def __init__(self) -> None:
        alice: Player = Player("Alice")
        bob: Player = Player("Bob")
        self.env: BaseEnvironment = BaseEnvironment([alice, bob])
        self.seats: list[Optional[SessionSeat]] = [None, None]
        self.vis: SimpleVisualization = SimpleVisualization()    

    def connect(self) -> Optional[PlayerController]:
        main_log.info("Trying to seat a new player at session")
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
        cont = PlayerController(player, player_log)
        self.seats[seat_position] = SessionSeat(self.env, cont)
        return cont
    
    def run_game(self) -> None:
        while not self.env.game_over:
            main_log.debug("tick game")
            seats_filled: bool = reduce(operator.and_ ,map(lambda seat: seat is not None, self.seats), True)
            if not seats_filled: 
                main_log.debug("Waiting for more players...")
                time.sleep(0.3)
                continue
            # Blockes until active player chooses an action 
            intended_action: Optional[str] = self.demand_action_event_from_active_player()
            if intended_action is None:
                main_log.error("Got no action intent from active player!")            
            assert intended_action is not None
            # Apply action to environment
            self.env.step(self.env.get_active_player(), intended_action)
            self.vis.step(self.env)
            self.prepare_next_player_action()

        main_log.info("Game concluded. Shutting down session!")
        return
    
    def demand_action_event_from_active_player(self) -> Optional[str]:
        active_seat: Optional[SessionSeat] = self.get_active_seat()
        if active_seat is None:
            return 
        assert active_seat is not None
        active_seat.controller.upcoming_action = self.env.get_upcoming_action()
        active_seat.controller.intended_next_action = None
        # Wait for player input
        while active_seat.controller.intended_next_action is None:
            time.sleep(0.1)
        player_intent: str = active_seat.controller.intended_next_action
        active_seat.reset_controller()
        return player_intent
    
    def prepare_next_player_action(self) -> None:
        active_seat: Optional[SessionSeat] = self.get_active_seat()
        assert active_seat is not None
        active_seat.controller.upcoming_action=self.env.get_upcoming_action()
        return
    
    def get_active_seat(self) -> Optional[SessionSeat]:
        if self.seats[0] is None or self.seats[1] is None:
            main_log.error("Can't get active seat because a player disconnected!")
            return
        for seat in self.seats:
            assert seat is not None
            if self.env.get_active_player() == seat.controller.player: 
                return seat
        main_log.error("Active Player {} does not belong to any connected seat!".format(self.env.get_active_player()))
        return

