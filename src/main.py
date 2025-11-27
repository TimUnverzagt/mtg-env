from environment.base import BaseEnvironment as MtgEnv
from environment.player import Player
import environment.constants as MtgEnvConst
from rendering.simple import SimpleVisualization
from server.multi_client_session import MultiClientSession as GameSession
from agents.simple import Goldfish

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
    turns_started: int= 0
    vis: SimpleVisualization = SimpleVisualization()    
    agent1: Goldfish = Goldfish(session)
    time.sleep(3)
    agent2: Goldfish = Goldfish(session)
    time.sleep(2)

    logger.info("Started Game")

#    vis.step(env)
#    while not env.game_over:
#        turns_started += 1
#        logger.info("Starting Turn {}".format(turns_started))
#        env.step(alice, (0, MtgEnvConst.MAINPHASE_PASS))
#        vis.step(env)
#        env.step(alice, (1, MtgEnvConst.COMBAT_ATTACK))
#        vis.step(env)
#        env.step(bob, (0, MtgEnvConst.MAINPHASE_PASS))
#        vis.step(env)
#        env.step(bob, (1, MtgEnvConst.COMBAT_PASS))
#        print(env)
        
    logger.info("Finished Game")
    return 0


if __name__ == "__main__":
    main()