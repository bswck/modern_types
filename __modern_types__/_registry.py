"""Extra patching utilities for __modern_types__."""

from __future__ import annotations

import collections
import collections.abc
import contextlib
import sys
import typing


class PEP604:
    def __or__(self, other: Any) -> Any:
        return typing.Union[self, other]


class PEP604GenericAlias(typing._GenericAlias, PEP604, _root=True):  # type: ignore[call-arg,name-defined,misc] # noqa: SLF001
    def copy_with(self, params: Any) -> Any:
        return PEP604GenericAlias(
            self.__origin__,
            params,
            name=self._name,
            inst=self._inst,
        )


registry: dict[type[Any], PEP604GenericAlias] = {}


if sys.version_info[:2] == (3, 8):
    from functools import partial
    from typing import (  # type: ignore[attr-defined,unused-ignore]
        TYPE_CHECKING,
        TypeVar,
        _VariadicGenericAlias,
    )

    if TYPE_CHECKING:
        from typing import Any

    T = TypeVar("T")  # Any type.
    KT = TypeVar("KT")  # Key type.
    VT = TypeVar("VT")  # Value type.
    T_co = TypeVar("T_co", covariant=True)  # Any type covariant containers.
    V_co = TypeVar("V_co", covariant=True)  # Any type covariant containers.
    VT_co = TypeVar("VT_co", covariant=True)  # Value type covariant containers.
    T_contra = TypeVar("T_contra", contravariant=True)  # Ditto contravariant.
    # Internal type variable used for Type[].
    CT_co = TypeVar("CT_co", covariant=True, bound=type)

    class _PEP604VariadicGenericAlias(_VariadicGenericAlias, PEP604, _root=True):  # type: ignore[call-arg,misc,unused-ignore]
        def copy_with(self, params: Any) -> Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    _alias = partial(PEP604GenericAlias, special=True)

    # Default replacements for built-in types.
    registry.update(
        {
            collections.abc.Awaitable: _alias(collections.abc.Awaitable, T_co),
            collections.abc.Coroutine: _alias(
                collections.abc.Coroutine,
                (T_co, T_contra, V_co),
            ),
            collections.abc.AsyncIterable: _alias(collections.abc.AsyncIterable, T_co),
            collections.abc.AsyncIterator: _alias(collections.abc.AsyncIterator, T_co),
            collections.abc.Iterable: _alias(collections.abc.Iterable, T_co),
            collections.abc.Iterator: _alias(collections.abc.Iterator, T_co),
            collections.abc.Reversible: _alias(collections.abc.Reversible, T_co),
            collections.abc.Container: _alias(collections.abc.Container, T_co),
            collections.abc.Collection: _alias(collections.abc.Collection, T_co),
            collections.abc.Callable: _VariadicGenericAlias(  # type: ignore[dict-item,unused-ignore]
                collections.abc.Callable,
                (),
                special=True,
            ),
            collections.abc.Set: _alias(
                collections.abc.Set,
                T_co,
                name="AbstractSet",
            ),
            collections.abc.MutableSet: _alias(collections.abc.MutableSet, T),
            collections.abc.Mapping: _alias(collections.abc.Mapping, (KT, VT_co)),
            collections.abc.MutableMapping: _alias(
                collections.abc.MutableMapping,
                (KT, VT),
            ),
            collections.abc.Sequence: _alias(collections.abc.Sequence, T_co),
            collections.abc.MutableSequence: _alias(collections.abc.MutableSequence, T),
            tuple: _PEP604VariadicGenericAlias(tuple, (), special=True, name="Tuple"),
            list: _alias(list, T, name="List"),
            collections.deque: _alias(collections.deque, T, name="Deque"),
            set: _alias(set, T, name="Set"),
            frozenset: _alias(frozenset, T_co, name="FrozenSet"),
            collections.abc.MappingView: _alias(collections.abc.MappingView, T_co),
            collections.abc.KeysView: _alias(collections.abc.KeysView, KT),
            collections.abc.ItemsView: _alias(collections.abc.ItemsView, (KT, VT_co)),
            collections.abc.ValuesView: _alias(collections.abc.ValuesView, VT_co),
            contextlib.AbstractContextManager: _alias(
                contextlib.AbstractContextManager,
                T_co,
                name="ContextManager",
            ),
            contextlib.AbstractAsyncContextManager: _alias(
                contextlib.AbstractAsyncContextManager,
                T_co,
                name="AsyncContextManager",
            ),
            dict: _alias(dict, (KT, VT), name="Dict"),
            collections.defaultdict: _alias(
                collections.defaultdict,
                (KT, VT),
                name="DefaultDict",
            ),
            collections.OrderedDict: _alias(collections.OrderedDict, (KT, VT)),
            collections.Counter: _alias(collections.Counter, T),
            collections.ChainMap: _alias(collections.ChainMap, (KT, VT)),
            collections.abc.Generator: _alias(
                collections.abc.Generator,
                (T_co, T_contra, V_co),
            ),
            collections.abc.AsyncGenerator: _alias(
                collections.abc.AsyncGenerator,
                (T_co, T_contra),
            ),
            type: _alias(type, CT_co, name="Type"),
        },
    )

elif sys.version_info[:2] == (3, 9):
    from typing import (  # type: ignore[attr-defined,unused-ignore]
        TYPE_CHECKING,
        TypeVar,
        _CallableGenericAlias,
        _CallableType,
        _SpecialGenericAlias,
        _TupleType,
    )

    if TYPE_CHECKING:
        from typing import Any

    class _PEP604SpecialGenericAlias(_SpecialGenericAlias, PEP604, _root=True):  # type: ignore[call-arg,misc,unused-ignore]
        def copy_with(self, params: Any) -> Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    class _PEP604CallableGenericAlias(_CallableGenericAlias, PEP604, _root=True):  # type: ignore[call-arg,misc,unused-ignore]
        pass

    class _PEP604CallableType(_CallableType, PEP604, _root=True):  # type: ignore[call-arg,misc,unused-ignore]
        def copy_with(self, params: Any) -> Any:
            return _PEP604CallableGenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    class _PEP604TupleType(_TupleType, PEP604, _root=True):  # type: ignore[call-arg,misc,unused-ignore]
        def copy_with(self, params: Any) -> Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    _alias = _PEP604SpecialGenericAlias

    # Default replacements for built-in types.
    registry.update(
        {
            collections.abc.Awaitable: _alias(collections.abc.Awaitable, 1),
            collections.abc.Coroutine: _alias(collections.abc.Coroutine, 3),
            collections.abc.AsyncIterable: _alias(collections.abc.AsyncIterable, 1),
            collections.abc.AsyncIterator: _alias(collections.abc.AsyncIterator, 1),
            collections.abc.Iterable: _alias(collections.abc.Iterable, 1),
            collections.abc.Iterator: _alias(collections.abc.Iterator, 1),
            collections.abc.Reversible: _alias(collections.abc.Reversible, 1),
            collections.abc.Container: _alias(collections.abc.Container, 1),
            collections.abc.Collection: _alias(collections.abc.Collection, 1),
            collections.abc.Callable: _PEP604CallableType(collections.abc.Callable, 2),  # type: ignore[dict-item,unused-ignore]
            collections.abc.Set: _alias(collections.abc.Set, 1, name="AbstractSet"),
            collections.abc.MutableSet: _alias(collections.abc.MutableSet, 1),
            collections.abc.Mapping: _alias(collections.abc.Mapping, 2),
            collections.abc.MutableMapping: _alias(collections.abc.MutableMapping, 2),
            collections.abc.Sequence: _alias(collections.abc.Sequence, 1),
            collections.abc.MutableSequence: _alias(collections.abc.MutableSequence, 1),
            tuple: _PEP604TupleType(tuple, -1, name="Tuple"),
            list: _alias(list, 1, name="List"),
            collections.deque: _alias(collections.deque, 1, name="Deque"),
            set: _alias(set, 1, name="Set"),
            frozenset: _alias(frozenset, 1, name="FrozenSet"),
            collections.abc.MappingView: _alias(collections.abc.MappingView, 1),
            collections.abc.KeysView: _alias(collections.abc.KeysView, 1),
            collections.abc.ItemsView: _alias(collections.abc.ItemsView, 2),
            collections.abc.ValuesView: _alias(collections.abc.ValuesView, 1),
            contextlib.AbstractContextManager: _alias(
                contextlib.AbstractContextManager,
                1,
                name="ContextManager",
            ),
            contextlib.AbstractAsyncContextManager: _alias(
                contextlib.AbstractAsyncContextManager,
                1,
                name="AsyncContextManager",
            ),
            dict: _alias(dict, 2, name="Dict"),
            collections.defaultdict: _alias(
                collections.defaultdict,
                2,
                name="DefaultDict",
            ),
            collections.OrderedDict: _alias(collections.OrderedDict, 2),
            collections.Counter: _alias(collections.Counter, 1),
            collections.ChainMap: _alias(collections.ChainMap, 2),
            collections.abc.Generator: _alias(collections.abc.Generator, 3),
            collections.abc.AsyncGenerator: _alias(collections.abc.AsyncGenerator, 2),
            type: _alias(type, 1, name="Type"),
        },
    )


def register(
    ref: str,
    type_vars: object | tuple[object, ...],
    *,
    noop_ok: bool = False,
) -> None:
    """Register a patch for a class importable from `ref`."""
    module_name, name = ref.partition(".")[::2]
    try:
        module = sys.modules[module_name]
    except KeyError:
        if noop_ok:
            return
        msg = f"Module {module_name} must be imported before __modern_types__ patching"
        raise ValueError(msg) from None
    try:
        old_obj = getattr(module, name)
    except AttributeError:
        if noop_ok:
            return
        raise

    if isinstance(old_obj, type):
        registry[old_obj] = PEP604GenericAlias(old_obj, type_vars)
