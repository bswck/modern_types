"""Replacement registry for the type hint visitor."""

from __future__ import annotations

import collections
import collections.abc
import sys
import typing
from contextlib import AbstractAsyncContextManager as _AContextManager
from contextlib import AbstractContextManager as _ContextManager
from functools import update_wrapper


class PEP604Link:
    """Base class for type proxies."""

    def __or__(self, other: typing.Any) -> typing.Any:
        return Union[create_dest_alias(self), create_dest_alias(other)]

    def __ror__(self, other: typing.Any) -> typing.Any:
        return Union[create_dest_alias(other), create_dest_alias(self)]


class PEP604Proxy(PEP604Link):
    """Base class for type proxies."""

    def __init__(self, proxied_type: object, orig_name: str, new_name: str) -> None:
        self.__proxied_type__ = proxied_type
        self.__orig_name__ = orig_name
        self.__new_name__ = new_name

    def __create_dest_alias__(self) -> Any:
        return self.__proxied_type__

    def __repr__(self) -> str:
        return (
            f"<PEP604 proxy {self.__orig_name__!r}->{self.__new_name__!r} "
            f"({self.__proxied_type__})>"
        )


class PEP604GenericAliasLink(typing._GenericAlias, PEP604Link, _root=True):  # type: ignore[call-arg,name-defined,misc] # noqa: SLF001
    def __init__(self, dest: Any, parameters: Any) -> None:
        self.__dest__ = dest
        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        self.__dest_parameters__ = parameters

    def __create_dest_alias__(self) -> Any:
        return self.__dest__[(*map(create_dest_alias, self.__dest_parameters__),)]

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__create_dest_alias__(), name)

    def copy_with(self, params: typing.Any) -> typing.Any:
        return PEP604GenericAliasLink(
            dest=self.__dest__,
            parameters=params,
        )


def create_dest_alias(obj: object) -> Any:
    """Try to create a runtime-valid alias out of the one from the type hint visitor."""
    factory = getattr(obj, "__create_dest_alias__", None)
    if callable(factory):
        return factory()
    return obj


global_registry: dict[object, object] = {}


_PYTHON_VERSION = sys.version_info[:2]

if typing.TYPE_CHECKING or _PYTHON_VERSION >= (3, 10):  # pragma: no cover
    from typing import *  # noqa: F403

elif not typing.TYPE_CHECKING and _PYTHON_VERSION < (3, 10):  # pragma: no cover

    class TypingLink(PEP604Link):
        def __init__(self, dest: Any) -> None:
            update_wrapper(self, dest)
            self.__dest__ = dest

        def __create_dest_alias__(self) -> Any:
            return self.__dest__

        def __getitem__(self, parameters: typing.Any) -> typing.Any:
            return PEP604GenericAliasLink(self.__dest__, parameters)

    Any = TypingLink(typing.Any)
    Union = TypingLink(typing.Union)
    Optional = TypingLink(typing.Optional)
    Literal = TypingLink(typing.Literal)

    Awaitable = TypingLink(typing.Awaitable)
    Coroutine = TypingLink(typing.Coroutine)
    AsyncIterable = TypingLink(typing.AsyncIterable)
    AsyncIterator = TypingLink(typing.AsyncIterator)
    Iterable = TypingLink(typing.Iterable)
    Iterator = TypingLink(typing.Iterator)
    Reversible = TypingLink(typing.Reversible)
    Container = TypingLink(typing.Container)
    Collection = TypingLink(typing.Collection)
    Callable = TypingLink(typing.Callable)
    AbstractSet = TypingLink(typing.AbstractSet)
    MutableSet = TypingLink(typing.MutableSet)
    Mapping = TypingLink(typing.Mapping)
    MutableMapping = TypingLink(typing.MutableMapping)
    Sequence = TypingLink(typing.Sequence)
    MutableSequence = TypingLink(typing.MutableSequence)
    Tuple = TypingLink(typing.Tuple)
    List = TypingLink(typing.List)
    Deque = TypingLink(typing.Deque)
    Set = TypingLink(typing.Set)
    FrozenSet = TypingLink(typing.FrozenSet)
    MappingView = TypingLink(typing.MappingView)
    KeysView = TypingLink(typing.KeysView)
    ItemsView = TypingLink(typing.ItemsView)
    ValuesView = TypingLink(typing.ValuesView)
    ContextManager = TypingLink(typing.ContextManager)
    AsyncContextManager = TypingLink(typing.AsyncContextManager)
    Dict = TypingLink(typing.Dict)
    DefaultDict = TypingLink(typing.DefaultDict)
    OrderedDict = TypingLink(typing.OrderedDict)
    Counter = TypingLink(typing.Counter)
    ChainMap = TypingLink(typing.ChainMap)
    Generator = TypingLink(typing.Generator)
    AsyncGenerator = TypingLink(typing.AsyncGenerator)
    Type = TypingLink(typing.Type)


global_registry.update(
    {
        collections.abc.Awaitable: Awaitable,
        collections.abc.Coroutine: Coroutine,
        collections.abc.AsyncIterable: AsyncIterable,
        collections.abc.AsyncIterator: AsyncIterator,
        collections.abc.Iterable: Iterable,
        collections.abc.Iterator: Iterator,
        collections.abc.Reversible: Reversible,
        collections.abc.Container: Container,
        collections.abc.Collection: Collection,
        collections.abc.Callable: Callable,
        collections.abc.Set: AbstractSet,
        collections.abc.MutableSet: MutableSet,
        collections.abc.Mapping: Mapping,
        collections.abc.MutableMapping: MutableMapping,
        collections.abc.Sequence: collections.abc.Sequence,
        collections.abc.MutableSequence: collections.abc.MutableSequence,
        tuple: Tuple,
        list: List,
        collections.deque: Deque,
        set: Set,
        frozenset: FrozenSet,
        collections.abc.MappingView: MappingView,
        collections.abc.KeysView: KeysView,
        collections.abc.ItemsView: ItemsView,
        collections.abc.ValuesView: ValuesView,
        _ContextManager: ContextManager,
        _AContextManager: AsyncContextManager,
        dict: Dict,
        collections.defaultdict: DefaultDict,
        collections.OrderedDict: OrderedDict,
        collections.Counter: Counter,
        collections.ChainMap: ChainMap,
        collections.abc.Generator: Generator,
        collections.abc.AsyncGenerator: AsyncGenerator,
        type: Type,
        typing.Any: Any,
        typing.Union: Union,
        typing.Optional: Optional,
        typing.Literal: Literal,
    },
)


def register(
    ref: str,
    type_vars: object | tuple[object, ...],
    *,
    noop_ok: bool = False,
    overwrite: bool = False,
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

    if overwrite or (isinstance(old_obj, type) and old_obj not in global_registry):
        global_registry[old_obj] = PEP604GenericAliasLink(
            typing._GenericAlias(old_obj, type_vars),  # type: ignore[attr-defined]  # noqa: SLF001
            type_vars,
        )
