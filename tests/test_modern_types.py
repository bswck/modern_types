from __future__ import annotations

from typing import Dict, List, Set, Tuple, FrozenSet, Union, get_type_hints

import __modern_types__


def test_modern_types() -> None:
    class Foo:
        a: dict[str, int]
        b: list[int]
        c: set[int]
        d: tuple[int, ...] | None
        e: frozenset[int]

    assert get_type_hints(Foo) == {
        "a": Dict[str, int],
        "b": List[int],
        "c": Set[int],
        "d": Union[Tuple[int, ...], None],
        "e": FrozenSet[int],
    }
