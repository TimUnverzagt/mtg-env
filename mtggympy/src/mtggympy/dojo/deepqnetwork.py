import torch
import torch.nn as nn
import torch.nn.functional as F

from collections import deque, namedtuple
import random
from typing import Any
class DeepQNetwork(nn.Module):

    def __init__(self, n_observations: int, n_actions: int) -> None:
        super(DeepQNetwork, self).__init__()
        self.layer1: nn.Linear = nn.Linear(n_observations, 128)
        self.layer2: nn.Linear = nn.Linear(128, 128)
        self.layer3: nn.Linear = nn.Linear(128, n_actions)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        print(x.shape)
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)


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