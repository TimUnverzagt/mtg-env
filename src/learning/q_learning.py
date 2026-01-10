from collections import defaultdict
import numpy as np
from numpy.typing import NDArray
from server.api import MtgObservation, MtgAction, MtgEnv
from typing import cast, DefaultDict, TypeAlias
from tqdm import tqdm 
from logging_config import main_log

QValue: TypeAlias = np.float32
MtgActionSpace: TypeAlias = NDArray[np.int8]

#def flatten_action(action_coordinates: MtgAction, dimension_sizes: list[int]) -> FlatMtgAction:
#    flat_index: FlatMtgAction = np.int8(0)
#    shift_size_from_prev_dimensions = 1
#    for coord, dim_size in zip(reversed(action_coordinates), reversed(dimension_sizes)):
#        flat_index += coord * shift_size_from_prev_dimensions
#        shift_size_from_prev_dimensions *= dim_size
#    return flat_index

#def unflatten_action(flat_index: FlatMtgAction, dimension_sizes: list[int]) -> MtgAction:
#    assert all(d > 0 for d in dimension_sizes)
#    assert 0 <= flat_index < prod(dimension_sizes)
#
#    action: list[int] = []
#    for dim_size in reversed(dimension_sizes):
#        action.append(cast(int, flat_index) % dim_size)
#        flat_index //= dim_size
#    return cast(MtgAction, tuple(reversed(action)))

class QLearner:
    def __init__(
        self,
        env: MtgEnv,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        """Initialize a Q-Learning agent.

        Args:
            env: The training environment
            learning_rate: How quickly to update Q-values (0-1)
            initial_epsilon: Starting exploration rate (usually 1.0)
            epsilon_decay: How much to reduce epsilon each episode
            final_epsilon: Minimum exploration rate (usually 0.1)
            discount_factor: How much to value future rewards (0-1)
        """
        self.env = env

        self.q_values: DefaultDict[MtgObservation, MtgActionSpace] = defaultdict(lambda: np.zeros(2, int))

        self.lr = learning_rate
        self.discount_factor = discount_factor  # How much we care about future rewards

        # Exploration parameters
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        # Track learning progress
        self.training_error: list[QValue] = []

    def learn(self, no_of_episodes: int):
        for episode in tqdm(range(no_of_episodes)):
            main_log.info(50 * "-")
            main_log.info(21 * "-" + " Episode {}".format(episode) +  21 * "-")
            main_log.info(50 * "-")
            # Start a new hand
            obs, _ = self.env.reset()
            main_log.info("Started Game")
            done = False

            # Play one complete game
            while not done:
                # Agent chooses action (initially random, gradually more intelligent)
                action: MtgAction = self.get_action(obs)

                # Take action and observe result
                next_obs, reward, terminated, truncated, _ = self.env.step(action)

                # Learn from this experience
                self.update(obs, action, reward, terminated, next_obs)

                # Move to next state
                done = terminated or truncated
                obs = next_obs


            main_log.info("Finished Game")
            # Reduce exploration rate (agent becomes less random over time)
            self.decay_epsilon()
        print(self.q_values)

    def get_action(self, obs: MtgObservation) -> MtgAction:
        """Choose an action using epsilon-greedy strategy.

        Returns:
            action: 0 (pass) or 1 (take some action)
        """
        # With probability epsilon: explore (random action)
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()

        # With probability (1-epsilon): exploit (best known action)
        else:
            return (cast(int, np.argmax(self.q_values[obs])),)

    def update(
        self,
        obs: MtgObservation,
        action: MtgAction,
        reward: int,
        terminated: bool,
        next_obs: MtgObservation,
    ):
        """Update Q-value based on experience.

        This is the heart of Q-learning: learn from (state, action, reward, next_state)
        """
        # What's the best we could do from the next state?
        # (Zero if episode terminated - no future rewards possible)
        future_q_value: QValue  = QValue((not terminated) * np.max(self.q_values[next_obs]))

        # What should the Q-value be? (Bellman equation)
        target: QValue = reward + self.discount_factor * future_q_value

        # How wrong was our current estimate?
        temporal_difference: QValue = target - self.q_values[obs][action]

        # Update our estimate in the direction of the error
        # Learning rate controls how big steps we take
        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.lr * temporal_difference
        )

        # Track learning progress (useful for debugging)
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        """Reduce exploration rate after each episode."""
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)