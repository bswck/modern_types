from __future__ import annotations

import collections.abc
import importlib
import re
import sys
import warnings
from collections import defaultdict
from typing import (
    DefaultDict,
    Dict,
    FrozenSet,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    get_type_hints,
)

import pytest

warnings.simplefilter("ignore", DeprecationWarning)
import __modern_types__
from __modern_types__ import _WARNING_3_10

warnings.simplefilter("default", DeprecationWarning)

class Foo:
    a: dict[str, int]
    b: list[int]
    c: set[int]
    d: tuple[int, ...] | None
    e: frozenset[int]
    f: defaultdict[str, int]
    g: str | None
    h: str | int
    i: str | int | None
    j: str
    k: collections.abc.Mapping[str, int]
    l: collections.abc.Mapping[str, int] | None
    m: collections.abc.Mapping[str, int | None] | float | None


_PYTHON_VERSION = sys.version_info[:2]  # without PATCH version


if _PYTHON_VERSION <= (3, 9):
   def test_modern_types() -> None:
        assert get_type_hints(Foo, globals(), locals()) == {
            "a": Dict[str, int],
            "b": List[int],
            "c": Set[int],
            "d": Optional[Tuple[int, ...]],
            "e": FrozenSet[int],
            "f": DefaultDict[str, int],
            "g": Optional[str],
            "h": Union[str, int],
            "i": Optional[Union[str, int]],
            "j": str,
            "k": Mapping[str, int],
            "l": Optional[Mapping[str, int]],
            "m": Union[Mapping[str, Optional[int]], float, None],
        }
else:
    # Handling 3.10+ versions is intended to ensure that the library
    # continues to work with future Python versions.
    def test_warning() -> None:
        with pytest.warns(DeprecationWarning, match=re.escape(_WARNING_3_10)):
            importlib.reload(__modern_types__)


if __name__ == "__main__":
    print(type(get_type_hints(Foo, globals(), locals())["k"]).mro())