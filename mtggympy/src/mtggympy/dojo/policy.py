import torch
import torch.nn as nn
import torch.nn.functional as F

from collections import deque, namedtuple
import random
from typing import Any

from mtggympy.api.gym import encoding
class MultiheadNetwork(nn.Module):

    def __init__(self, n_observation_dims: int) -> None:
        super(MultiheadNetwork, self).__init__()
        self.base_encoder: nn.Linear = nn.Linear(n_observation_dims, 256)
        self.action_index_head: nn.Linear = nn.Linear(256, encoding.ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS)

        self.extended_encoder: nn.Linear = nn.Linear(256 + encoding.ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS, 256)
        self.action_param_head: nn.Linear = nn.Linear(256, encoding.ASSUMED_MAX_ARGUMENTS_SIZE)
        self.param_threshold: nn.Threshold = nn.Threshold(0.5, 0)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        encoded: torch.Tensor = F.relu(self.base_encoder(x))
        action_logits: torch.Tensor = F.relu(self.action_index_head(encoded))
        encoded_with_action: torch.Tensor = F.relu(self.extended_encoder(torch.cat([encoded, action_logits], dim=1)))
        all_action_params: torch.Tensor = F.relu(self.action_param_head(encoded_with_action))
        selected_action_params: torch.Tensor = self.param_threshold(all_action_params)
        return action_logits.squeeze(), selected_action_params.squeeze()


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward')) # type: ignore


class ReplayMemory(object):

    def __init__(self, capacity:int):
        self.memory:deque[Any] = deque([], maxlen=capacity)

    def push(self, *args): # type: ignore
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size:int):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)