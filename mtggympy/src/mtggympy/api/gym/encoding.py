from __future__ import annotations
from typing import Any, TypeAlias
from gymnasium.spaces import Discrete, MultiDiscrete, Tuple
import numpy as np
from numpy.typing import NDArray
from more_itertools import collapse

ASSUMED_INITIAL_DECK_SIZE = 40
ASSUMED_MAX_BATTLEFIELD_SIZE = ASSUMED_INITIAL_DECK_SIZE
ASSUMED_INITIAL_HP = 20
ASSUMED_MAX_HAND_SIZE = 8 #Because players can draw a card before discarding
ASSUMED_MAX_TURNS = ASSUMED_INITIAL_DECK_SIZE
ASSUMED_NUMBER_OF_CARDS = 20
ASSUMED_NUMBER_OF_PLAYER_EVENTS = 3
ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS = 3
ASSUMED_MAX_ARGUMENTS_SIZE = ASSUMED_MAX_BATTLEFIELD_SIZE*ASSUMED_MAX_BATTLEFIELD_SIZE


MtgCardObs: TypeAlias = NDArray[np.int8]
CARD_ENCODING_LIMIT: MtgCardObs = np.array([
    ASSUMED_NUMBER_OF_CARDS,
    1, #Tapped bool
    1 #Attacking bool
])
CARD_DIMS = 3

# information type at external border of server 
MtgSelfObs: TypeAlias = tuple[
    int, #hp
    int, #lib size
    NDArray[np.int8], #cards in hand
    NDArray[np.int8]] #cards in play
SELF_OBS_ENCODING_LIMIT: MtgSelfObs = (
    ASSUMED_INITIAL_HP,
    ASSUMED_INITIAL_DECK_SIZE,
    np.tile(CARD_ENCODING_LIMIT, (ASSUMED_MAX_HAND_SIZE ,1 )),
    np.tile(CARD_ENCODING_LIMIT, (ASSUMED_MAX_BATTLEFIELD_SIZE ,1 ))
)
SELF_OBS_DIMS: int =  2 + CARD_DIMS * ASSUMED_MAX_HAND_SIZE + CARD_DIMS * ASSUMED_MAX_BATTLEFIELD_SIZE

MtgOppObs: TypeAlias = tuple[
    int, #hp
    int, #lib size
    int, #hand size
    np.ndarray] #cards in play
OPP_OBS_ENCODING_LIMIT: MtgOppObs = (
    ASSUMED_INITIAL_HP,
    ASSUMED_INITIAL_DECK_SIZE,
    ASSUMED_MAX_HAND_SIZE,
    np.concatenate((CARD_ENCODING_LIMIT, np.array([ASSUMED_MAX_BATTLEFIELD_SIZE])))
)
OPP_OBS_DIMS= 3 + CARD_DIMS * ASSUMED_MAX_BATTLEFIELD_SIZE

MtgObservation: TypeAlias = tuple[
    int, #seat
    int, #turn
    int, #playerevent
    int, #bool self is active player
    MtgSelfObs, 
    MtgOppObs]
OBSERVATION_ENCODING_LIMIT: MtgObservation = (
    1,
    ASSUMED_MAX_TURNS,
    ASSUMED_NUMBER_OF_PLAYER_EVENTS-1,
    1,
    SELF_OBS_ENCODING_LIMIT,
    OPP_OBS_ENCODING_LIMIT
)
OBSERVATION_DIMS: int = 4 + SELF_OBS_DIMS + OPP_OBS_DIMS
FlatMtgObservation: TypeAlias = NDArray[Any]


def flatten_observation(obs: MtgObservation) -> FlatMtgObservation:
    return np.array(list(collapse(obs)))

MtgAction: TypeAlias = tuple[
    int, # id
    NDArray[np.int8]] # action arguments
ACTION_ENCODING_LIMIT: MtgAction = (
    ASSUMED_MAX_NUMBER_OF_POSSIBLE_ACTIONS - 1,
    np.full(ASSUMED_MAX_ARGUMENTS_SIZE,1)
    # the biggest argument space covers pairing over all possible battlefield positions
    # for shape-conformity all other argument spaces can be extended to this size
)
ACTION_DIMS: int = 1+ASSUMED_MAX_BATTLEFIELD_SIZE*ASSUMED_MAX_BATTLEFIELD_SIZE
FlatMtgAction: TypeAlias = NDArray[Any]
MtgInfo: TypeAlias = dict[str, Any]
    
def explode_flat_action(flat_action: FlatMtgAction) -> MtgAction:
    assert len(flat_action) == ACTION_DIMS
    nested_action: MtgAction = (
        flat_action[0],
        np.reshape(flat_action[1:ACTION_DIMS],
                        shape=(ASSUMED_MAX_BATTLEFIELD_SIZE, ASSUMED_MAX_BATTLEFIELD_SIZE))
    )
    return nested_action
    

def flatten_action(action: MtgAction) -> FlatMtgAction:
    return np.array(list(collapse(action)))

    
def flatten_tuple_of_discrete_spaces(space: Tuple) -> MultiDiscrete:
    dimension_sizes: list[int] = []
    for child in space.spaces: # type: ignore
        if isinstance(child, Discrete):
            dimension_sizes.append(int(child.n))
        elif isinstance(child, MultiDiscrete):
            for dim_size in np.ndarray.flatten(child.nvec):
                dimension_sizes.append(int(dim_size))
        elif isinstance(child, Tuple):
            compacted_space: MultiDiscrete = flatten_tuple_of_discrete_spaces(child)
            for dim_size in np.ndarray.flatten(compacted_space.nvec):
                dimension_sizes.append(int(dim_size))

    #print("Number of dimensions in flattened space: {}".format(len(dimension_sizes)))
    return MultiDiscrete(dimension_sizes, dtype=np.int8)


def get_space_sizes(space: Tuple) -> list[int]:
    dimensions: list[int] = []
    for child in space.spaces: # type: ignore
        if isinstance(child, Discrete):
            dimensions.append(1)
        elif isinstance(child, MultiDiscrete):
            dimensions.append(len(np.ndarray.flatten(child.nvec)))
        elif isinstance(child, Tuple):
            dimensions += get_space_sizes(child)
    return dimensions