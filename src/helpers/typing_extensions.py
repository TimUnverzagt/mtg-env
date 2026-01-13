from typing import TypeGuard, TypeVar, Mapping, Any, Union, Tuple, TypeAlias

M = TypeVar("M", bound=Mapping[Any, Any])


def union_narrows_to_nested_map(value: object | M) -> TypeGuard[M]:
    return isinstance(value, Mapping)

T = TypeVar("T")
Tree: TypeAlias = Union[T, Tuple["Tree[T]", ...]]