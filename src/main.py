from api.wrapper import MtgWrapper as Env
from api.wrapper import MtgObservation
from helpers.type_guards import union_narrows_to_nested_map
# from agents.console import ConsoleAgent

#import time
#import sys

from logging_config import main_log

def main():
    """ Main program """
    for i in range(5):
        main_log.info(50 * "-")
        main_log.info(21 * "-" + " Epoch {}".format(i) +  21 * "-")
        main_log.info(50 * "-")
        play_game()
        
    return 0

def play_game() -> None:
    main_log.info("Setup Env-Wrapper")
    environment: Env = Env()
    last_obs: MtgObservation = environment.reset()[0]
    main_log.info("Started Game")
    while not environment.game_session.game_state.game_over:
        intended_action: int = 0
        assert union_narrows_to_nested_map(last_obs["upcoming_decision"])
        event_index: int = last_obs["upcoming_decision"]["upcoming_decision_event"]  
        if event_index == 0:
            intended_action = 0
        if event_index == 1:
            intended_action = 1
        
        last_obs = environment.step({"decision_event": event_index, "decision_index": intended_action})[0]

    main_log.info("Finished Game")


if __name__ == "__main__":
    main()