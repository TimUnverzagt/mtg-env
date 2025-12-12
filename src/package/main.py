from server.multi_client_session import MultiClientSession as GameSession
from agents.simple import Goldfish, Monkey
# from agents.console import ConsoleAgent
from threading import Thread

import time
#import sys

from package.logging_config import main_log

def main():
    """ Main program """
    for i in range(10):
        main_log.info(50 * "-")
        main_log.info(21 * "-" + " Epoch {}".format(i) +  21 * "-")
        main_log.info(50 * "-")
        play_game()
        
    return 0

def play_game() -> None:
    main_log.info("Setup GameSession")
    session: GameSession = GameSession()
    main_log.info("Started Game")

    session_thread: Thread = Thread(target=session.run_game)
    session_thread.start()

    agent1: Goldfish = Goldfish(session)
    agent1_thread: Thread = Thread(target=agent1.play_game, daemon=True)
    agent1_thread.start()
    time.sleep(0)
    agent2: Monkey = Monkey(session)
    agent2_thread: Thread = Thread(target=agent2.play_game, daemon=True)
    agent2_thread.start()
    time.sleep(0.2)
    
    session_thread.join()
    main_log.info("Finished Game")


if __name__ == "__main__":
    main()