from __future__ import annotations
from typing import Callable, Generic, ParamSpec, TypeVar, Any, Concatenate, TYPE_CHECKING
from environment import constants as const

if TYPE_CHECKING:
    from environment.base import BaseEnvironment as MtgEnv
    from environment.player import Player


P = ParamSpec("P")
T = TypeVar("T")


class ActionReplacement(Generic[P, T]):

    def __init__(self,
                 input_action: Callable[Concatenate[Player, P], T],
                 replacing_action: Callable[Concatenate[Player, P], T]):
        self.input_action = input_action
        self.replacing_action = replacing_action
        return


class ActionProxy:
    def __init__(self, env: MtgEnv):
        self.env = env
        self.replacement_catalog: dict[str, ActionReplacement[Any, Any]] = {
            const.DECKING: ActionReplacement(env.draw_card, env.kill_player_by_decking)
        }
    
    def _execute_action_with_replacment(self, actor: Player, attempted_action: Callable[Concatenate[Player, P], T], 
                       *args: P.args, **kwargs: P.kwargs) -> T:
        
        if attempted_action == self.replacement_catalog[const.DECKING].input_action \
        and actor.cards_in_library <= 0:
            return self.replacement_catalog[const.DECKING].replacing_action(actor, *args, **kwargs)
        
        return attempted_action(actor, *args, **kwargs)
    
    def execute_action(self, actor: Player, attempted_action: Callable[Concatenate[Player, P], T], 
                       *args: P.args, **kwargs: P.kwargs) -> T:
        action_result: T = self._execute_action_with_replacment(actor, attempted_action, *args, **kwargs)
        self.env.update_game_state()
        return action_result

    

    

