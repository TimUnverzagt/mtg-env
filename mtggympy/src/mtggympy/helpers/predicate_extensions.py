from typing import TypeVar
from mtggympy.helpers.typing_extensions import Predicate

T = TypeVar("T")

def build_either_predicate(first: Predicate, second: Predicate) -> Predicate:
    return lambda: first() or second()