from mtggympy.gameengine.constants import GameStep
from mtggympy.gameengine.state.event import ActionData, ActionIntent, PlayerEvent, event_from_step
from mtggympy.gameengine.state.core import GameState
from mtggympy.server.session.player_controller import PlayerController
import mtggympy.gameengine.transition as GameEngine
#from game.state import GameState
from mtggympy.gameengine.state.defaults import PlayerState
from mtggympy.server.session.obfuscation import observe_game_state

import time
from functools import reduce
from typing import Optional
import operator
import mtggympy.app_config as conf
from copy import deepcopy

from mtggympy.logging_config import session_log as logger

def get_next_step(previous_step: GameStep, intent: ActionIntent) -> GameStep:
    match previous_step:
        case GameStep.UPKEEP:
            return GameStep.DRAW
        case GameStep.DRAW:
            return GameStep.MAIN_1
        case GameStep.MAIN_1:
            return GameStep.ATTACK_STEP if (intent.action is ActionData.PASS) else GameStep.MAIN_1
        case GameStep.ATTACK_STEP:
            return GameStep.BLOCK_STEP
        case GameStep.BLOCK_STEP:
            return GameStep.MAIN_2
        case GameStep.MAIN_2:
            return GameStep.END_STEP if (intent.action is ActionData.PASS) else GameStep.MAIN_2
        case GameStep.END_STEP:
            return GameStep.UPKEEP



class MultiClientSession():

    def __init__(self) -> None:
        self.game_state = GameEngine.get_initial_game_state()
        self.seats: list[Optional[PlayerController]] = [None, None]
        self.vis: None = None
        if conf.HUMAN_RENDERING:
            #TODO: Connect to UI
            pass
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
        player_info: PlayerState = self.game_state.player_states[seat_position]
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

            step_success: bool
            target_seat: int 
            match self.game_state.step:
                case GameStep.UPKEEP | GameStep.DRAW  | GameStep.END_STEP:
                    step_success = self.step_without_player(self.game_state)
                case GameStep.MAIN_1 | GameStep.ATTACK_STEP | GameStep.MAIN_2:
                    # Retrieve Player
                    target_seat = self.get_seat_from_active_player_onward()
                    cont: Optional[PlayerController] = self.get_controller_for_target_seat(target_seat)
                    if cont is None: 
                        continue
                    assert cont is not None
                    step_success = self.step_with_player(self.game_state, cont, target_seat, event_from_step(self.game_state.step))
                case GameStep.BLOCK_STEP: 
                    # Retrieve Player
                    target_seat = self.get_seat_from_active_player_onward(seat_offseat=1)
                    cont: Optional[PlayerController] = self.get_controller_for_target_seat(target_seat)
                    if cont is None: 
                        continue
                    assert cont is not None
                    step_success = self.step_with_player(self.game_state, cont, target_seat, event_from_step(self.game_state.step))
            if not step_success:
                    logger.warning("Step Resolution was unsuccessful. This may result in a corrupted game state")

            if(conf.HUMAN_RENDERING):
                #assert self.vis is not None
                #self.vis.step(self.game_state)
                #TODO: Integrate human gui here
                logger.error("RENDERING is currently NOT IMPLEMENTED")
                pass
        logger.info("Game concluded. Shutting down session!")
        self.shutting_down = True
        for cont in self.seats:
            assert cont is not None
            with cont.obs_before_action_condition:
                cont.obs_before_action_condition.notify_all()
        return
    
    def step_without_player(self, game_state: GameState) -> bool:
        step_success: bool
        match game_state.step:
            case GameStep.MAIN_1 | GameStep.ATTACK_STEP | GameStep.BLOCK_STEP | GameStep.MAIN_2:
                return False
            case GameStep.UPKEEP:
                step_success = GameEngine.upkeep(game_state)
            case GameStep.DRAW:
                step_success = GameEngine.draw_step(game_state)
            case GameStep.END_STEP:
                step_success = GameEngine.end_step(game_state)
                step_success &= GameEngine.pass_turn(game_state)
        succesor_step: GameStep = get_next_step(game_state.step, ActionIntent(ActionData.PASS, None))
        if (succesor_step is not game_state.step):
            GameEngine.empty_mana_pools(game_state)
        game_state.step = succesor_step
        return step_success
    
    def step_with_player(self, game_state: GameState, cont: PlayerController, player_seat: int, player_event: PlayerEvent) -> bool:
            # Prompt Player Input
            with cont.obs_before_action_condition:
                logger.debug("SessionTick: {}: Waiting for player to have no prior state before starting".format(cont.player_info.name))
                cont.obs_before_action_condition.wait_for(lambda: cont.obs_before_action is None)
                logger.debug("SessionTick: {}: Prompting Player with state {}".format(
                    cont.player_info.name,
                    game_state
                    ))
                logger.info("SessionTick: {}: Prompting Player with event {}".format(
                    cont.player_info.name,
                    player_event.name
                    ))
                cont.set_action_priors(observe_game_state(game_state, player_seat))
                cont.obs_before_action_condition.notify_all()                
                cont.obs_before_action_condition.wait_for(lambda: cont.obs_before_action is None)

            # Await Player Input
            logger.debug("SessionTick: {}: Waiting for Player Input".format(cont.player_info.name))
            with cont.intent_condition:
                cont.intent_condition.wait_for(lambda: cont.intent is not None)
                if not cont.intent:
                    return False
                player_intent: ActionIntent = cont.intent
                    
                # Process Player Input and report state update
                logger.debug("SessionTick: {}: Received Player Input: {} --- {}".format(cont.player_info.name, player_intent.action.name, player_intent.parameters))
                step_success: bool
                match game_state.step:
                    case GameStep.UPKEEP | GameStep.DRAW:
                        step_success = False                    
                    case GameStep.END_STEP:
                        step_success = GameEngine.end_step(game_state)
                        step_success &= GameEngine.pass_turn(game_state)
                    case GameStep.MAIN_1:
                        step_success = GameEngine.main_phase(game_state.active_player_index, player_intent, game_state)
                    case GameStep.ATTACK_STEP:
                        step_success = GameEngine.declare_attackers_step(game_state.active_player_index, player_intent, game_state)
                    case GameStep.BLOCK_STEP:
                        acting_seat_index: int = self.get_seat_from_active_player_onward(seat_offseat=1)
                        step_success = GameEngine.declare_blockers_step(acting_seat_index, player_intent, game_state)
                    case GameStep.MAIN_2:
                        step_success = GameEngine.main_phase(game_state.active_player_index, player_intent, game_state)
                if step_success:
                    succesor_step: GameStep = get_next_step(game_state.step, player_intent)
                    if (succesor_step is not game_state.step):
                        GameEngine.empty_mana_pools(game_state)
                    game_state.step = succesor_step
                cont.intent = None
                cont.intent_condition.notify_all()

            # Return result
            with cont.obs_after_action_condition:
                cont.set_action_result(observe_game_state(game_state, player_seat))
                cont.obs_after_action_condition.notify_all()
                cont.obs_after_action_condition.wait_for(lambda: cont.obs_after_action is None)
                logger.debug("SessionTick: {}: Answered player with new state {}".format(
                    cont.player_info.name,
                    game_state
                ))
            return step_success

    def get_controller_for_target_seat(self, target_seat: int) -> Optional[PlayerController]:
        if self.seats[0] is None or self.seats[1] is None:
            logger.error("Can't get active controller because a player disconnected!")
            return
        
        target_player_info: PlayerState = self.game_state.player_states[target_seat]
        for controller in self.seats:
            assert controller is not None
            if target_player_info == controller.player_info: 
                return controller
        logger.error("PlayerInfo does not align with any controller! This should never happen!!")

    def get_seat_from_active_player_onward(self, seat_offseat: int = 0) -> int:
        return (self.game_state.active_player_index + seat_offseat) % len(self.game_state.player_states)

