from typing import cast


import gymnasium as gym

import math
import random
from gymnasium.spaces import MultiDiscrete
import matplotlib
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import count

import tqdm

from mtggympy.api.gym.encoding import FlatMtgAction, FlatMtgObservation
from mtggympy.api.gym.environment import StandaloneEnv
from mtggympy.dojo.policy import MultiheadNetwork, ReplayMemory, Transition

device = torch.device("cpu")

# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

plt.ion() # type: ignore

BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.01
EPS_DECAY = 2500
TAU = 0.005
LR = 3e-4

env: gym.Env[FlatMtgObservation, FlatMtgAction] = StandaloneEnv()
#n_action_dims: int = len(cast(MultiDiscrete, env.action_space).nvec)
n_obs_dims: int = len(cast(MultiDiscrete, env.observation_space).nvec)

policy_net = MultiheadNetwork(n_obs_dims).to(device)
target_net = MultiheadNetwork(n_obs_dims).to(device)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(10000)

steps_done = 0

def select_action(state: torch.Tensor):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    #print("State shape during select_action:{}".format(state.shape))
    if sample > eps_threshold:
        with torch.no_grad():
            action_logits, action_params = policy_net(state)
            return torch.cat([action_logits.argmax().expand(1), action_params])
    else:
        return torch.tensor(env.action_space.sample(), device=device, dtype=torch.long)


episode_durations: list[int] = []


def plot_durations(show_result: bool=False):
    plt.figure(1) #type: ignore
    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    if show_result:
        plt.title('Result') #type: ignore
    else:
        plt.clf()
        plt.title('Training...') #type: ignore
    plt.xlabel('Episode') #type: ignore
    plt.ylabel('Duration') #type: ignore
    plt.plot(durations_t.numpy()) #type: ignore
    # Take 100 episode averages and plot them too
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy()) #type: ignore

    plt.pause(0.001)  # pause a bit so that plots are updated
    if is_ipython:
        if not show_result:
            display.display(plt.gcf()) #type: ignore
            display.clear_output(wait=True) #type: ignore
        else:
            display.display(plt.gcf()) #type: ignore

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch: Transition = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool) # type: ignore
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None]) # type: ignore
    state_batch = torch.cat(batch.state) # type: ignore
    action_batch = torch.cat(batch.action) # type: ignore
    reward_batch = torch.cat(batch.reward) # type: ignore

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_macro_action_values, _ = policy_net(state_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        macro_values,_ = target_net(non_final_next_states)
        next_state_values[non_final_mask] = macro_values.max(dim=1).values
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_macro_action_values.max(dim=1).values.unsqueeze(1), expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step() # type: ignore


def train(num_episodes: int) -> None:
    for _ in tqdm.tqdm(range(num_episodes)):
        # Initialize the environment and get its state
        state, _ = env.reset()
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        for t in count():
            action = select_action(state)
            observation, reward, terminated, truncated, _ = env.step(torch.flatten(action))
            reward = torch.tensor([reward], device=device)
            done = terminated or truncated

            if terminated:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

            # Store the transition in memory
            memory.push(state, action, next_state, reward) # type: ignore

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            optimize_model()

            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = target_net.state_dict()
            policy_net_state_dict = policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            target_net.load_state_dict(target_net_state_dict)

            if done:
                episode_durations.append(t + 1)
                plot_durations()
                break
    print('Complete')
    plot_durations(show_result=True)
    plt.ioff() # type: ignore
    plt.show() # type: ignore

if __name__ == "__main__":
    train(num_episodes=50)