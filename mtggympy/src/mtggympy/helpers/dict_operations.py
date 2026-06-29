from typing import TypeVar

T = TypeVar("T")
S = TypeVar("S")

def can_fit_second_dict_into_first_by_value(first: dict[T, int], second: dict[T, int]) -> bool:
    fits_so_far: bool = True
    for key in second:
        if not first.get(key):
            return False
        fits_so_far &= (first[key] >= second[key])
    return fits_so_far


def dicts_equal_with_default(first: dict[T, S], second: dict[T, S]):
    keys: set[T] = set(first) | set(second)
    return all(first[key] == second[key] for key in keys)