from environment.base import BaseEnvironment as MtgEnv
from environment.player import Player
import environment.constants as MtgEnvConst

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
    logger.info("Started")
    alice: Player = Player("Alice")
    bob: Player = Player("Bob")
    env: MtgEnv = MtgEnv([alice, bob])

    for i in range(0, 5):
        logger.info("Starting Turn {}".format(i+1))
        env.step(alice, (0, MtgEnvConst.MAINPHASE_PASS))
        env.step(alice, (1, MtgEnvConst.COMBAT_ATTACK))
        env.step(bob, (0, MtgEnvConst.MAINPHASE_PASS))
        env.step(bob, (1, MtgEnvConst.COMBAT_PASS))
        print(env)

    logger.info("Finished")
    return 0

if __name__ == "__main__":
    main()