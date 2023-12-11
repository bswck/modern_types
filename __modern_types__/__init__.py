"""
__modern_types__.

`__modern_types__` aims to provide [PEP 585](https://peps.python.org/pep-0585/) + [PEP 604](https://peps.python.org/pep-0604/) backports for Python <=3.10 deferred type evaluation backward compatibility.

(C) 2023-present Bartosz Sławecki (bswck)
"""
from __future__ import annotations

import collections
import inspect
import sys
import typing
from typing import _GenericAlias  # type: ignore[attr-defined]

from __modern_types__._monkeypatch import MONKEYPATCH_STACK_OFFSET, monkeypatch

__all__ = (
    "monkeypatch",
    # "AliasBase"?
    # "builtin_scope_overrides"?
)

_PYTHON_VERSION = sys.version_info[:2]  # without PATCH version
_WARNING_3_10 = "You do not need to import __modern_types__ on Python >=3.10."

if _PYTHON_VERSION < (3, 10):

    class AliasBase:
        """PEP 604 backport. Subclass check fix."""

        __origin__: typing.Any

        def __subclasscheck__(self, cls: typing.Any) -> typing.Any:
            return self.__origin__.__subclasscheck__(cls)

        def __or__(self, other: type[typing.Any]) -> typing.Any:
            """Implement | operator for X | Y type syntax."""
            return typing.Union[self, other]  # pragma: no cover; coverage bug?

    _GenericAlias.__bases__ += (AliasBase,)
    _GenericAlias.__subclasscheck__ = AliasBase.__subclasscheck__

    for _g in (
        typing.Tuple,
        typing.List,
        typing.Set,
        typing.FrozenSet,
        typing.Dict,
        typing.Type,
    ):
        _g._inst = True  # type: ignore[attr-defined]  # noqa: SLF001

    builtin_scope_overrides = {
        "tuple": typing.Tuple,
        "list": typing.List,
        "set": typing.Set,
        "frozenset": typing.FrozenSet,
        "dict": typing.Dict,
        "type": typing.Type,
    }

    _typing_eval_type = typing._eval_type  # noqa: SLF001

    def _wrap_eval_type(
        obj: typing.Any,
        globalns: dict[str, typing.Any] | None = None,
        localns: dict[str, typing.Any] | None = None,
        recursive_guard: typing.Any = None,
    ) -> dict[str, typing.Any]:
        """PEP 585 & PEP 604 backport."""
        return _typing_eval_type(
            obj,
            {**builtin_scope_overrides, **(globalns or {})},
            localns,
            *(() if _PYTHON_VERSION == (3, 8) else (recursive_guard or frozenset(),)),
        )

    _collections_defaultdict = collections.defaultdict
    collections.defaultdict = typing.DefaultDict  # type: ignore[misc]

    typing._eval_type = typing.cast(typing.Any, _wrap_eval_type)  # noqa: SLF001

    # We are very kind and we will fixup `get_type_hints` for all modules that import us.
    # To overcome this, make a reference that wraps `get_type_hints` in some other object.
    stack_offset = 1

    for offset, frame_info in enumerate(inspect.stack()):
        if __name__ in "".join(frame_info.code_context or ()):
            stack_offset = offset
            importer = sys.modules[frame_info.frame.f_globals["__name__"]]
            for key, val in vars(importer).items():
                if val is _typing_eval_type:
                    setattr(importer, key, _wrap_eval_type)
                if val is _collections_defaultdict:
                    setattr(importer, key, typing.DefaultDict)

    MONKEYPATCH_STACK_OFFSET.set(stack_offset)

    # Automatically patch other modules
    import __modern_types__._auto  # noqa: F401
else:
    import warnings

    warnings.warn(_WARNING_3_10, category=DeprecationWarning, stacklevel=-1)
