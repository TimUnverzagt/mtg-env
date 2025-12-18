from __future__ import annotations
from typing import Callable, Generic, ParamSpec, TypeVar, Any, Concatenate, TYPE_CHECKING
from game import constants as const
from game.state import GameState
import game.engine as env

if TYPE_CHECKING:
    import package.game.engine as env


AdditionalParam = ParamSpec("AdditionalParam")
ActionResult = TypeVar("ActionResult")


class ActionReplacement(Generic[AdditionalParam, ActionResult]):

    def __init__(self,
                 input_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult],
                 replacing_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult]):
        self.input_action = input_action
        self.replacing_action = replacing_action
        return


class ActionProxy:
    def __init__(self):
        self.replacement_catalog: dict[str, ActionReplacement[Any, Any]] = {
            const.DECKING: ActionReplacement(env.draw_card, env.kill_player_by_decking)
        }
    
    def _execute_action_with_replacment(self, acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                       *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
        
        if attempted_action == self.replacement_catalog[const.DECKING].input_action \
        and game_state.player_infos[acting_seat].cards_in_library <= 0:
            return self.replacement_catalog[const.DECKING].replacing_action(acting_seat, game_state, *args, **kwargs)
        
        return attempted_action(acting_seat, game_state, *args, **kwargs)
    
    def execute_action(self, acting_seat: int, game_state: GameState, attempted_action: Callable[Concatenate[int, GameState, AdditionalParam], ActionResult], 
                       *args: AdditionalParam.args, **kwargs: AdditionalParam.kwargs) -> ActionResult:
        action_result: ActionResult = self._execute_action_with_replacment(acting_seat, game_state, attempted_action, *args, **kwargs)
        env.update_game_state(game_state)
        return action_result

    

    

