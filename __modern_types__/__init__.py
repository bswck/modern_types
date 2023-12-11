"""
__modern_types__.

PEP 585 + PEP 604 backports, because it started becoming annoying.

(C) 2023-present Bartosz Sławecki (bswck)
"""
from __future__ import annotations

import builtins
import typing

for g in (
    typing.Tuple,
    typing.List,
    typing.Set,
    typing.FrozenSet,
    typing.Dict,
    typing.Type,
):
    g._inst = True  # type: ignore[attr-defined]  # noqa: SLF001


class PEP604:
    """PEP 604 backport."""

    def __or__(self, other: type[typing.Any]) -> typing.Any:
        """Implement | operator for X | Y type syntax."""
        return typing.Union[self, other]


typing._GenericAlias.__bases__ += (PEP604,)  # type: ignore[attr-defined]  # noqa: SLF001


vars(builtins).update(
    {
        "tuple": typing.Tuple,
        "list": typing.List,
        "set": typing.Set,
        "frozenset": typing.FrozenSet,
        "dict": typing.Dict,
    },
)
