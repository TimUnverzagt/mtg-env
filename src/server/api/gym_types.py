from typing import Any

# information type at external border of server 
type MtgObservation = tuple[int, int, int, MtgPlayerObs, MtgPlayerObs]
type MtgAction = tuple[int]
type MtgInfo = dict[str, Any]
type MtgPlayerObs = tuple[int, int, int]
