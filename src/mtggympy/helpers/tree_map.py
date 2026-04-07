from helpers.typing_extensions import Tree
from typing import Callable, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

def tree_map(
    f: Callable[[T, U], V],
    a: Tree[T],
    b: Tree[U],
) -> Tree[V]:
    if isinstance(a, tuple) and isinstance(b, tuple):
        ta = cast(tuple[Tree[T], ...], a)
        tb = cast(tuple[Tree[U], ...], b)
        return tuple(tree_map(f, x, y) for x, y in zip(ta, tb))
    if not isinstance(a, tuple) and not isinstance(b, tuple):
        return f(a, b)
    raise TypeError("Tree shape mismatch")