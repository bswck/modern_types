from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, FrozenSet, List, Set, Tuple, Union, get_type_hints

import __modern_types__


def test_modern_types() -> None:
    class Foo:
        a: dict[str, int]
        b: list[int]
        c: set[int]
        d: tuple[int, ...] | None
        e: frozenset[int]
        f: defaultdict[str, int]

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
