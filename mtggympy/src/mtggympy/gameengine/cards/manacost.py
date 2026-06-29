
from collections import defaultdict
from dataclasses import dataclass

from mtggympy.gameengine.constants import ManaColor


@dataclass(init=False)
class ManaCost():
    def __init__(self, fixed_cost: dict[ManaColor, int], generic_cost: int) -> None:
        self.fixed_cost: dict[ManaColor, int] = defaultdict(lambda: 0)
        for key, value in fixed_cost.items():
            self.fixed_cost[key] = value
        self.generic_cost = generic_cost


    
    
