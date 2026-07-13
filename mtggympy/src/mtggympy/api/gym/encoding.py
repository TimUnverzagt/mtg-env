from typing import Any, TypeAlias
import numpy as np
from numpy.typing import NDArray

ASSUMED_INITIAL_DECK_SIZE = 40
ASSUMED_MAX_BATTLEFIELD_SIZE = ASSUMED_INITIAL_DECK_SIZE
ASSUMED_INITIAL_HP = 20
ASSUMED_MAX_HAND_SIZE = 8 #Because players can draw a card before discarding
ASSUMED_MAX_TURNS = ASSUMED_INITIAL_DECK_SIZE
ASSUMED_NUMBER_OF_CARDS = 20
ASSUMED_NUMBER_OF_PLAYER_EVENTS = 3
ASSUMED_NUMBER_OF_ACTIONS = 5


MtgCardObs: TypeAlias = NDArray[np.int8]
CARD_ENCODING_LIMIT: MtgCardObs = np.array([
    ASSUMED_NUMBER_OF_CARDS,
    1, #Tapped bool
    1 #Attacking bool
])

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

MtgOppObs: TypeAlias = tuple[
    int, #hp
    int, #lib size
    int, #hand size
    np.ndarray] #cards in play
OPP_OBS_ENCODING_LIMIT: MtgOppObs = (
    ASSUMED_INITIAL_HP,
    ASSUMED_INITIAL_DECK_SIZE,
    ASSUMED_MAX_HAND_SIZE,
    np.tile(CARD_ENCODING_LIMIT, (ASSUMED_MAX_BATTLEFIELD_SIZE ,1 ))
)

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

MtgAction: TypeAlias = tuple[
    int, # id
    NDArray[np.int8]] # action arguments
ACTION_ENCODING_LIMIT: MtgAction = (
    ASSUMED_NUMBER_OF_ACTIONS - 1,
    np.full((ASSUMED_MAX_BATTLEFIELD_SIZE, ASSUMED_MAX_BATTLEFIELD_SIZE),1)
    # the biggest argument space covers pairing over all possible battlefield positions
    # for shape-conformity all other argument spaces can be extended to this size
)
MtgInfo: TypeAlias = dict[str, Any]
