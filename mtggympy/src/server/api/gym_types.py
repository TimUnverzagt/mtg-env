from typing import Any, TypeAlias

# information type at external border of server 
MtgPlayerObs: TypeAlias = tuple[int, int, int]
MtgObservation: TypeAlias = tuple[int, int, int, MtgPlayerObs, MtgPlayerObs]
MtgAction: TypeAlias = tuple[int]
MtgInfo: TypeAlias = dict[str, Any]
