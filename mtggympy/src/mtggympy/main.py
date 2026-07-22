from threading import Thread
#from mtggympy.api.gym.environment import StandaloneEnv
from mtggympy.api.dektop.app import DesktopApp
#from mtggympy.server.agents.simple import Goldfish, Monkey
from mtggympy.server.agents.constants import InternalAgentType
from mtggympy.server.agents.rulesbased import RulesBasedAgent
from mtggympy.server.session.multi_client import MultiClientSession as MtgSession
#from api.wrapper import MtgObservation
import mtggympy.dojo.internal_matches as bot_match
import mtggympy.dojo.training as training

# from agents.console import ConsoleAgent

#import time
#import sys

#from logging_config import main_log
import mtggympy.config.app_config as conf

def learning_example():
    training.train(50)

def desktop_game_example():
    session: MtgSession = MtgSession() 
    session_thread: Thread = Thread(target=session.tick_session, daemon=False)
    session_thread.start()
    opponent = RulesBasedAgent(session, "Opp-RulesBased", target_seat=1) 
    opponent_thread: Thread = Thread(target=opponent.play_game, daemon=True)
    opponent_thread.start()
    game: DesktopApp = DesktopApp(session, "Tim", take_input_from_gui=True)
    game.start()


if __name__ == "__main__":
    match conf.CURRENT_SETUP:
        case conf.Setup.HUMAN_VS_INTERNALS:
            desktop_game_example()
        case conf.Setup.Q_TRAINING:
            learning_example()
        case conf.Setup.GOLDFISH_SPEED_EXP:
            bot_match.fight_two_player(conf.EPISODES_IN_EXPERIMENT, (InternalAgentType.GOLDFISH, InternalAgentType.GOLDFISH))
        case conf.Setup.MONKEY_SPEED_EXP:
            bot_match.fight_two_player(conf.EPISODES_IN_EXPERIMENT, (InternalAgentType.MONKEY, InternalAgentType.MONKEY))
        case conf.Setup.RULESBASED_SPEED_EXP:
            bot_match.fight_two_player(conf.EPISODES_IN_EXPERIMENT, (InternalAgentType.RULESBASED, InternalAgentType.RULESBASED))

    