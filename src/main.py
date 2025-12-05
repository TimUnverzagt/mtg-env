from server.multi_client_session import MultiClientSession as GameSession
from agents.simple import Goldfish, Monkey
# from agents.console import ConsoleAgent
from threading import Thread

import time
#import sys

from logging_config import main_log

def main():
    """ Main program """

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
    return 0


if __name__ == "__main__":
    main()