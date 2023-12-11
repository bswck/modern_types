from __future__ import annotations

import sys
from collections import defaultdict
from typing import DefaultDict, Dict, FrozenSet, List, Set, Tuple, Union, get_type_hints
from typing import TypeVar

from __modern_types__ import patch

class Foo:
    a: dict[str, int]
    b: list[int]
    c: set[int]
    d: tuple[int, ...] | None
    e: frozenset[int]
    f: defaultdict[str, int]


if sys.version_info[:2] <= (3, 9):
    ListType = list

    T = TypeVar("T")

    def test_patch() -> None:
        patch(__name__ + ".ListType", T)  # TODO(bswck): support variadic generics
        assert ListType[int] == List[int]

if sys.version_info[:2] <= (3, 8):
   def test_modern_types() -> None:
        assert defaultdict() == {}
        assert defaultdict is DefaultDict
        assert get_type_hints(Foo, globals(), locals()) == {
            "a": Dict[str, int],
            "b": List[int],
            "c": Set[int],
            "d": Union[Tuple[int, ...], None],
            "e": FrozenSet[int],
            "f": DefaultDict[str, int],
        }
elif sys.version_info[:2] == (3, 9):
    def test_modern_types() -> None:
        assert defaultdict is not DefaultDict  # replacement was not needed
        assert get_type_hints(Foo, globals(), locals()) == {
            "a": Dict[str, int],
            "b": List[int],
            "c": Set[int],
            "d": Union[Tuple[int, ...], None],
            "e": FrozenSet[int],
            "f": defaultdict[str, int],
        }
else:
    # Handling 3.10+ versions is intended to ensure that the library
    # continues to work with future Python versions.
    # TODO(bswck): Raise a warning when running on Python 3.10+.
    def test_dummy() -> None:
        pass
