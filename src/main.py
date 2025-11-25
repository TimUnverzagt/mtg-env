from environment.base import BaseEnvironment as MtgEnv
from environment.player import Player
import environment.constants as MtgEnvConst
from rendering.simple import SimpleVisualization

import keyboard
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

    logger.info("Setup Game")
    alice: Player = Player("Alice")
    bob: Player = Player("Bob")
    env: MtgEnv = MtgEnv([alice, bob])
    turns_started: int= 0
    vis: SimpleVisualization = SimpleVisualization()    

    logger.info("Started Game")
    while not env.game_over:
        turns_started += 1
        logger.info("Starting Turn {}".format(turns_started))
        env.step(alice, (0, MtgEnvConst.MAINPHASE_PASS))
        env.step(alice, (1, MtgEnvConst.COMBAT_ATTACK))
        env.step(bob, (0, MtgEnvConst.MAINPHASE_PASS))
        env.step(bob, (1, MtgEnvConst.COMBAT_PASS))
        print(env)
        vis.render_environment(env)
        keyboard.wait('enter')
        
    logger.info("Finished Game")
    return 0

if __name__ == "__main__":
    main()