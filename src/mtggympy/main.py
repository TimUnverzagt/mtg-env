from server.api.gym_environment import MtgEnv
#from api.wrapper import MtgObservation
from dojo.q_learning import QLearner

# from agents.console import ConsoleAgent

#import time
#import sys

#from logging_config import main_log

def main():
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


if __name__ == "__main__":
    main()