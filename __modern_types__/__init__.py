"""
__modern_types__.

PEP 585 + PEP 604 backports, because it started becoming annoying.

(C) 2023-present Bartosz Sławecki (bswck)
"""
from __future__ import annotations

import collections
import inspect
import sys
import typing
from typing import _GenericAlias  # type: ignore[attr-defined]

from __modern_types__._patch import patch

__all__ = (
    # "builtin_scope_overrides",
    "patch",
    # "PEP604",
)

if sys.version_info <= (3, 9):

    class PEP604:
        """PEP 604 backport."""

        def __or__(self, other: type[typing.Any]) -> typing.Any:
            """Implement | operator for X | Y type syntax."""
            return typing.Union[self, other]  # pragma: no cover; coverage bug?

    _GenericAlias.__bases__ += (PEP604,)

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

    _typing_get_type_hints = typing.get_type_hints

    def _wrap_get_type_hints(
        obj: typing.Any,
        globalns: dict[str, typing.Any] | None = None,
        localns: dict[str, typing.Any] | None = None,
    ) -> dict[str, typing.Any]:
        """PEP 585 backport."""
        return _typing_get_type_hints(
            obj,
            {**builtin_scope_overrides, **(globalns or {})},
            localns,
        )

    _collections_defaultdict = collections.defaultdict
    collections.defaultdict = typing.DefaultDict  # type: ignore[misc]
    typing.get_type_hints = typing.cast(typing.Any, _wrap_get_type_hints)

    # We are very kind and we will fixup `get_type_hints` for all modules that import us.
    # To overcome this, make a reference that wraps `get_type_hints` in some other object.
    for frame_info in inspect.stack():
        if __name__ in "".join(frame_info.code_context or ()):
            importer = sys.modules[frame_info.frame.f_globals["__name__"]]
            for key, val in vars(importer).items():
                if val is _typing_get_type_hints:
                    setattr(importer, key, _wrap_get_type_hints)
                if val is _collections_defaultdict:
                    setattr(importer, key, typing.DefaultDict)
