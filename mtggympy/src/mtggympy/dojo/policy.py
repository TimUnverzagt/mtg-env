import torch
import torch.nn as nn
import torch.nn.functional as F

from collections import deque, namedtuple
import random
from typing import Any


# Multiclass (multiple exlusive actions)
class ActionSelectionNetwork(nn.Module):
    def __init__(self, input_dims: int, output_dims: int) -> None:
        super(ActionSelectionNetwork, self).__init__()
        self.base_encoder: nn.Linear = nn.Linear(input_dims, 256)
        self.selection_layer: nn.Linear = nn.Linear(256, output_dims)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded: torch.Tensor = F.relu(self.base_encoder(x))
        action_logits: torch.Tensor = F.relu(self.selection_layer(encoded))
        return action_logits.squeeze()
    
# Multilabel (multiple non exclusive target selections)
class ActionParameterNetwork(nn.Module):
    def __init__(self, input_dims: int, output_dims: int) -> None:
        super(ActionParameterNetwork, self).__init__()
        self.base_encoder: nn.Linear = nn.Linear(input_dims, 256)
        self.selection_layer: nn.Linear = nn.Linear(256, output_dims)
        self.value_layer: nn.Linear = nn.Linear(256+output_dims, output_dims)
        self.loss = nn.BCELoss()
        #self.param_threshold: nn.Threshold = nn.Threshold(0.5, 0)
        return
    
    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if len(x.shape) <= 1:
            x = x.unsqueeze(dim=0)
        encoded: torch.Tensor = F.relu(self.base_encoder(x))
        parameter_selections: torch.Tensor = F.sigmoid(self.selection_layer(encoded))
        full_transition_intent: torch.Tensor = torch.cat([encoded, parameter_selections], dim=1)
        parameter_values: torch.Tensor = F.relu(self.value_layer(full_transition_intent))
        return parameter_selections.squeeze(), parameter_values.squeeze()
    
# Binary (two exlusive chocies: legal, nonlegal)
class ActionRejectionNetwork(nn.Module):
    def __init__(self, input_dims: int) -> None:
        super(ActionRejectionNetwork, self).__init__()
        self.base_encoder: nn.Linear = nn.Linear(input_dims, 256)
        self.legality_layer: nn.Linear = nn.Linear(256, 1)
        self.loss = nn.BCEWithLogitsLoss()
        return
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded: torch.Tensor = F.relu(self.base_encoder(x))
        legality_deduction: torch.Tensor = F.sigmoid(self.legality_layer(encoded))
        return legality_deduction
    
Transition = namedtuple('Transition',
                        ('state', 'action', 'params', 'next_state', 'reward', 'action_rejected')) # type: ignore


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