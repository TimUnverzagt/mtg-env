from server.player_connection import SessionSeat
from server.player_connection import PlayerController
from environment.base import BaseEnvironment
from environment.player import Player
from rendering.simple import SimpleVisualization

import time
from functools import reduce
from typing import Optional
import operator
import logging
logger = logging.getLogger(__name__)


class MultiClientSession:

    def __init__(self) -> None:
        alice: Player = Player("Alice")
        bob: Player = Player("Bob")
        self.env: BaseEnvironment = BaseEnvironment([alice, bob])
        self.seats: list[Optional[SessionSeat]] = [None, None]
        self.vis: SimpleVisualization = SimpleVisualization()    

    def connect(self) -> Optional[PlayerController]:
        logger.info("Trying to connect to connect to session")
        if self.seats[0] is None:
            return self.connect_to_seat(0)
        if self.seats[1] is None:
            return self.connect_to_seat(1)
        return
    
    def connect_to_seat(self, seat_position: int) -> Optional[PlayerController]:
        if seat_position >= len(self.seats):
            return
        if self.seats[seat_position] is not None:
            return
        player: Player = self.env.players[seat_position]
        cont = PlayerController(player)
        self.seats[seat_position] = SessionSeat(self.env, cont)
        return cont
    
    def run_game(self) -> None:
        while not self.env.game_over:
            logger.info("tick game")
            seats_filled: bool = reduce(operator.and_ ,map(lambda seat: seat is not None, self.seats), True)
            if not seats_filled: 
                logger.info("Waiting for more players...")
                time.sleep(0.3)
                continue
            # Blockes until active player chooses an action 
            intended_action: Optional[str] = self.demand_action_event_from_active_player()
            if intended_action is None:
                logger.error("Got no action intent from active player!")            
            assert intended_action is not None
            # Apply action to environment
            self.env.step(self.env.get_active_player(), intended_action)
            self.vis.step(self.env)
            self.prepare_next_player_action()

        logger.info("Game concluded. Shutting down session!")
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
            logger.error("Can't get active seat because a player disconnected!")
            return
        for seat in self.seats:
            assert seat is not None
            if self.env.get_active_player() == seat.controller.player: 
                return seat
        logger.error("Active Player {} does not belong to any connected seat!".format(self.env.get_active_player()))
        return

