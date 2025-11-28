from server.multi_client_session import MultiClientSession as GameSession
from agents.simple import Goldfish
from threading import Thread

import time
import sys
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """ Main program """

    logger.info("Setup GameSession")
    session: GameSession = GameSession()
    logger.info("Started Game")

    session_thread: Thread = Thread(target=session.run_game)
    session_thread.start()

    agent1: Goldfish = Goldfish(session)
    #TODO: Migrate Thread to PlayerController
    agent1_thread: Thread = Thread(target=agent1.play_game, daemon=True)
    agent1_thread.start()
    time.sleep(3)
    agent2: Goldfish = Goldfish(session)
    agent2_thread: Thread = Thread(target=agent2.play_game, daemon=True)
    agent2_thread.start()
    time.sleep(2)
    
    session_thread.join()
    logger.info("Finished Game")
    return 0


if __name__ == "__main__":
    main()