import gymnasium as gym

import math
import random
import matplotlib
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from itertools import count

import tqdm

import mtggympy.api.gym.encoding as encoding
from mtggympy.api.gym.encoding import FlatMtgAction, FlatMtgObservation
from mtggympy.api.gym.environment import StandaloneEnv, ACTION_REJECTED_INFO_KEY, ACTION_REJECTION_REWARD
from mtggympy.dojo.policy import ActionRejectionNetwork, ActionParameterNetwork, ActionSelectionNetwork, ReplayMemory, Transition

#Based on https://docs.pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

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

action_policy_net = ActionSelectionNetwork(encoding.OBSERVATION_DIMS, encoding.ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS).to(device)
action_look_ahead_net = ActionSelectionNetwork(encoding.OBSERVATION_DIMS, encoding.ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS).to(device)
action_look_ahead_net.load_state_dict(action_policy_net.state_dict())

param_policy_net = ActionParameterNetwork(encoding.OBSERVATION_DIMS + 1,
                                          encoding.ASSUMED_MAX_ARGUMENTS_SIZE)
param_look_ahead_net = ActionParameterNetwork(encoding.OBSERVATION_DIMS + 1,
                                          encoding.ASSUMED_MAX_ARGUMENTS_SIZE)
param_look_ahead_net.load_state_dict(param_policy_net.state_dict())

rejection_net = ActionRejectionNetwork(encoding.OBSERVATION_DIMS 
                                       + 1 # Selected Action 
                                       + encoding.ASSUMED_MAX_ARGUMENTS_SIZE)

action_optimizer = optim.AdamW(action_policy_net.parameters(), lr=LR, amsgrad=True)
param_optimizer = optim.AdamW(param_policy_net.parameters(), lr=LR, amsgrad=True)
rejection_optimizer = optim.AdamW(rejection_net.parameters(), lr=LR, amsgrad=True)
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
            action = action_policy_net(state.squeeze()).argmax().expand(1)
            params = param_policy_net(torch.cat([state.squeeze(),action]))[0] > 0.5
            return torch.cat([action, params])
    else:
        return torch.tensor(env.action_space.sample(), device=device, dtype=torch.long)


episode_rewards: list[int] = []
episode_lengths: list[int] = []
episode_illegal_actions: list[int] = []
episode_non_pass_actions: list[int] = []


def plot_durations(show_result: bool=False):
    plt.figure(1) #type: ignore
    rewards = torch.tensor(episode_rewards, dtype=torch.float) 
    if show_result:
        plt.title('Result') #type: ignore
    else:
        plt.clf()
        plt.title('Training...') #type: ignore
    plt.xlabel('Episode') #type: ignore
    plt.ylabel('Reward') #type: ignore
    plt.plot(rewards.numpy()) #type: ignore
    # Take 100 episode averages and plot them too
    if len(rewards) >= 100:
        means = rewards.unfold(0, 100, 1).mean(1).view(-1)
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
    action_rejected_batch = torch.cat(batch.action_rejected) # type: ignore

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    action_policy_values = action_policy_net(state_batch)
    intermediate_transition_batch = torch.cat([action_batch.unsqueeze(dim=1), state_batch], dim=1)
    param_policy_logits, param_policy_values = param_policy_net(intermediate_transition_batch)
    # Collect legality estimations for reward estimations
    full_transition_batch = torch.cat([intermediate_transition_batch, param_policy_logits > 0.5], dim=1)
    rejection_logits = rejection_net(full_transition_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    ################################
    # Value for action selection
    ################################
    next_state_action_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        action_look_ahead_values= action_look_ahead_net(non_final_next_states)
        action_look_ahead_selections = action_look_ahead_values.max(dim=1).indices
        action_look_ahead_max_values = action_look_ahead_values.max(dim=1).values
        next_state_action_values[non_final_mask] = action_look_ahead_max_values
    # Compute the expected Q values
    action_expected_compound_values = (next_state_action_values * GAMMA) + reward_batch
    ##################################
    # Value for parameter selection
    ##################################
    # Q for parameters is summed over all selected parameters
    # and normalized by the number of selected parameters to keep it in a similar 
    # order of magnitude to other value estimations without touching initilization
    next_state_param_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        intermediate_look_aheads = torch.cat([non_final_next_states, action_look_ahead_selections.unsqueeze(dim=1)], dim=1)
        param_look_ahead_logits, param_look_ahead_values = param_look_ahead_net(intermediate_look_aheads)
        param_look_ahead_selections = param_look_ahead_logits > 0.5
        param_look_ahead_normalized_values =  torch.mul(param_look_ahead_selections, param_look_ahead_values).sum(dim=1).div(param_look_ahead_selections.sum(dim=1))
        next_state_param_values[non_final_mask] = param_look_ahead_normalized_values
        full_transition_look_ahead = torch.cat([intermediate_look_aheads, param_look_ahead_logits], dim=1)
        rejection_look_ahead_labels = rejection_net(full_transition_look_ahead).max(dim=1).indices
        param_look_ahead_values[rejection_look_ahead_labels] = ACTION_REJECTION_REWARD
    # Compute the expected Q values
    param_expected_values = (next_state_param_values * GAMMA) + reward_batch

    # Compute loss
    rl_criterion = nn.SmoothL1Loss()
    action_loss = rl_criterion(action_policy_values.max(dim=1).values.unsqueeze(1), action_expected_compound_values.unsqueeze(1))
    param_policy_selections = param_policy_logits > 0.5
    param_policy_normalized_values =  torch.mul(param_policy_selections, param_policy_values).sum(dim=1).div(param_policy_selections.sum(dim=1))
    param_loss = rl_criterion(param_policy_normalized_values, param_expected_values)

    # Compute classification loss for action rejection net
    regression_criterion = rejection_net.loss
    rejection_loss = regression_criterion(rejection_logits.squeeze(), action_rejected_batch.to(torch.float))


    # Optimize the models
    action_optimizer.zero_grad()
    action_loss.backward()
    param_optimizer.zero_grad()
    param_loss.backward()
    rejection_optimizer.zero_grad()
    rejection_loss.backward()

    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(action_policy_net.parameters(), 100)
    torch.nn.utils.clip_grad_value_(param_policy_net.parameters(), 100)
    torch.nn.utils.clip_grad_value_(rejection_net.parameters(), 100)

    action_optimizer.step() # type: ignore
    param_optimizer.step() # type: ignore
    rejection_optimizer.step() #type: ignore


def train(num_episodes: int) -> None:
    for ep in tqdm.tqdm(range(num_episodes)):
        # Initialize the environment and get its state
        state, _ = env.reset()
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        cumulative_reward: int = 0
        cumulative_illegal_actions: int = 0
        cumulative_non_null_actions: int = 0
        cumulative_steps: int = 0
        for _ in count():
            action_rejected: bool = False
            action = select_action(state)
            if action[0] != 0:
                cumulative_non_null_actions += 1
            observation, reward, terminated, truncated, info = env.step(torch.flatten(action))
            cumulative_steps +=1
            cumulative_reward += reward
            if (ACTION_REJECTED_INFO_KEY in info) and info[ACTION_REJECTED_INFO_KEY]:
                action_rejected = True
                cumulative_illegal_actions += 1
            reward = torch.tensor([reward], device=device)
            done = terminated or truncated
            if terminated:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

            # Store the transition in memory
            memory.push(state, action[0].unsqueeze(dim=0), action[1:], next_state, reward, torch.tensor([action_rejected])) # type: ignore

            # Move to the next state
            state = next_state

            # Perform one step of the optimization (on the policy network)
            optimize_model()

            # Soft update of the look ahead network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            # Action selection
            action_look_ahead_state_dict = action_look_ahead_net.state_dict()
            action_policy_state_dict = action_policy_net.state_dict()
            for key in action_policy_state_dict:
                action_look_ahead_state_dict[key] = action_policy_state_dict[key]*TAU + action_look_ahead_state_dict[key]*(1-TAU)
            action_look_ahead_net.load_state_dict(action_look_ahead_state_dict)
            # Parameter selection
            param_look_ahead_state_dict = param_look_ahead_net.state_dict()
            param_policy_state_dict = param_policy_net.state_dict()
            for key in param_policy_state_dict:
                param_look_ahead_state_dict[key] = param_policy_state_dict[key]*TAU + param_look_ahead_state_dict[key]*(1-TAU)
            param_look_ahead_net.load_state_dict(param_look_ahead_state_dict)

            if done:
                episode_rewards.append(cumulative_reward)
                episode_lengths.append(cumulative_steps)
                episode_illegal_actions.append(cumulative_illegal_actions)
                episode_non_pass_actions.append(cumulative_non_null_actions)
                print("Episode: {}\nLength: {}\nReward: {}\nNon-Pass-Actions: {}\nIllegalActions: {}".format(
                    ep, cumulative_steps, cumulative_reward, cumulative_non_null_actions, cumulative_illegal_actions
                ))
                plot_durations()
                break
    print('Complete')
    plot_durations(show_result=True)
    plt.ioff() # type: ignore
    plt.show() # type: ignore

if __name__ == "__main__":
    train(num_episodes=50)