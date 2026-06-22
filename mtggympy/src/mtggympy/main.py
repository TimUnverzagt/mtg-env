from threading import Thread
from mtggympy.api.gym.environment import MtgEnv
from mtggympy.api.dektop.app import DesktopApp
#from mtggympy.server.agents.simple import Goldfish, Monkey
from mtggympy.server.agents.rulesbased import RulesBasedAgent
from mtggympy.server.session.multi_client import MultiClientSession as MtgSession
#from api.wrapper import MtgObservation
from mtggympy.dojo.q_learning import QLearner

# from agents.console import ConsoleAgent

#import time
#import sys

#from logging_config import main_log

def learning_example():
    no_of_episodes: int = 100
    start_epsilon: float = 1.0
    environment: MtgEnv = MtgEnv()
    learner: QLearner = QLearner(
        env=environment,
        learning_rate=0.1,
        initial_epsilon=start_epsilon,
        epsilon_decay = start_epsilon / (no_of_episodes * 3/4),
        final_epsilon=0.1
    )

    learner.learn(no_of_episodes)

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
    desktop_game_example()