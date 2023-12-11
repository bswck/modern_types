from __future__ import annotations

import importlib
import re
import sys
import warnings
from collections import defaultdict
from typing import get_type_hints
from typing import TypeVar

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


_PYTHON_VERSION = sys.version_info[:2]  # without PATCH version

if _PYTHON_VERSION <= (3, 9):
   def test_modern_types() -> None:
        assert get_type_hints(Foo, globals(), locals())
else:
    # Handling 3.10+ versions is intended to ensure that the library
    # continues to work with future Python versions.
    def test_warning() -> None:
        with pytest.warns(DeprecationWarning, match=re.escape(_WARNING_3_10)):
            importlib.reload(__modern_types__)
