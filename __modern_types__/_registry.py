"""Extra patching utilities for __modern_types__."""

from __future__ import annotations

import collections
import collections.abc
import sys
import typing
from contextlib import AbstractAsyncContextManager as _AContextManager
from contextlib import AbstractContextManager as _ContextManager
from functools import wraps


class PEP604:
    """Base class for type proxies."""

    def __or__(self, other: typing.Any) -> typing.Any:
        return Union[self, other]

    def __ror__(self, other: typing.Any) -> typing.Any:
        return Union[other, self]


class PEP604Proxy(PEP604):
    """Base class for type proxies."""

    def __init__(
        self,
        proxied_type: object,
        orig_name: str,
        new_name: str,
    ) -> None:
        self.proxied_type = proxied_type
        self.orig_name = orig_name
        self.new_name = new_name

    def __or__(self, other: typing.Any) -> typing.Any:
        return Union[self, other]

    def __ror__(self, other: typing.Any) -> typing.Any:
        return Union[other, self]

    def __repr__(self) -> str:
        return (
            f"<PEP604 proxy {self.orig_name!r}->{self.new_name!r} "
            f"({self.proxied_type})>"
        )


class PEP604GenericAlias(typing._GenericAlias, PEP604, _root=True):  # type: ignore[call-arg,name-defined,misc] # noqa: SLF001
    def copy_with(self, params: typing.Any) -> typing.Any:
        return PEP604GenericAlias(
            self.__origin__,
            params,
            name=self._name,
            inst=self._inst,
        )


global_registry: dict[object, object] = {}


_PYTHON_VERSION = sys.version_info[:2]

if typing.TYPE_CHECKING or _PYTHON_VERSION >= (3, 10):  # pragma: no cover
    from typing import *  # noqa: F403

elif not typing.TYPE_CHECKING and _PYTHON_VERSION == (3, 8):  # pragma: no cover
    from functools import partial
    from typing import (
        TypeVar,
        _SpecialForm,
        _VariadicGenericAlias,
    )

    T = TypeVar("T")
    KT = TypeVar("KT")
    VT = TypeVar("VT")
    T_co = TypeVar("T_co", covariant=True)
    V_co = TypeVar("V_co", covariant=True)
    VT_co = TypeVar("VT_co", covariant=True)
    T_contra = TypeVar("T_contra", contravariant=True)
    CT_co = TypeVar("CT_co", covariant=True, bound=type)

    class _PEP604VariadicGenericAlias(_VariadicGenericAlias, PEP604, _root=True):
        def copy_with(self, params: typing.Any) -> typing.Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    def _remove_dups_flatten(parameters: typing.Any) -> typing.Any:
        """Flattern Union among parameters, then remove duplicates."""
        # Flatten out Union[Union[...], ...].
        params = []
        for p in parameters:
            # We use local Union as a reference.
            if isinstance(p, typing._GenericAlias) and p.__origin__ is Union:  # noqa: SLF001
                params.extend(p.__args__)
            elif isinstance(p, tuple) and len(p) > 0 and p[0] is Union:
                params.extend(p[1:])
            else:
                params.append(p)
        # Weed out strict duplicates, preserving the first of each occurrence.
        all_params = set(params)
        if len(all_params) < len(params):
            new_params = []
            for t in params:
                if t in all_params:
                    new_params.append(t)
                    all_params.remove(t)
            params = new_params
            # assert not all_params, all_params
        return tuple(params)

    class _PEP604SpecialForm(_SpecialForm, PEP604, _root=True):
        def __getitem__(self, parameters: typing.Any) -> typing.Any:
            if self._name == "Union":
                if parameters == ():
                    msg = "Cannot take a Union of no types."
                    raise TypeError(msg)
                if not isinstance(parameters, tuple):
                    parameters = (parameters,)
                parameters = tuple(
                    parameter.proxied_type
                    if isinstance(parameter, PEP604Proxy)
                    else parameter
                    for parameter in parameters
                )
                msg = "Union[arg, ...]: each arg must be a type."
                parameters = tuple(typing._type_check(p, msg) for p in parameters)  # noqa: SLF001
                parameters = _remove_dups_flatten(parameters)
                if len(parameters) == 1:
                    return parameters[0]
            alias: typing.Any = super().__getitem__(parameters)
            return PEP604GenericAlias(alias.__origin__, alias.__args__)

    Any = _PEP604SpecialForm("Any", doc=typing.Any._doc)  # noqa: SLF001
    Union = _PEP604SpecialForm("Union", doc=typing.Union._doc)  # noqa: SLF001
    Optional = _PEP604SpecialForm("Optional", doc=typing.Optional._doc)  # noqa: SLF001
    Literal = _PEP604SpecialForm("Literal", doc=typing.Literal._doc)  # noqa: SLF001

    _pep604 = partial(PEP604GenericAlias, special=True)
    Awaitable = _pep604(collections.abc.Awaitable, T_co)
    Coroutine = _pep604(collections.abc.Coroutine, (T_co, T_contra, V_co))
    AsyncIterable = _pep604(collections.abc.AsyncIterable, T_co)
    AsyncIterator = _pep604(collections.abc.AsyncIterator, T_co)
    Iterable = _pep604(collections.abc.Iterable, T_co)
    Iterator = _pep604(collections.abc.Iterator, T_co)
    Reversible = _pep604(collections.abc.Reversible, T_co)
    Container = _pep604(collections.abc.Container, T_co)
    Collection = _pep604(collections.abc.Collection, T_co)
    Callable = _VariadicGenericAlias(collections.abc.Callable, (), special=True)
    AbstractSet = _pep604(collections.abc.Set, T_co, name="AbstractSet")
    MutableSet = _pep604(collections.abc.MutableSet, T)
    Mapping = _pep604(collections.abc.Mapping, (KT, VT_co))
    MutableMapping = _pep604(collections.abc.MutableMapping, (KT, VT))
    Sequence = _pep604(collections.abc.Sequence, T_co)
    MutableSequence = _pep604(collections.abc.MutableSequence, T)
    Tuple = _PEP604VariadicGenericAlias(tuple, (), special=True, name="Tuple")
    List = _pep604(list, T, name="List")
    Deque = _pep604(collections.deque, T, name="Deque")
    Set = _pep604(set, T, name="Set")
    FrozenSet = _pep604(frozenset, T_co, name="FrozenSet")
    MappingView = _pep604(collections.abc.MappingView, T_co)
    KeysView = _pep604(collections.abc.KeysView, KT)
    ItemsView = _pep604(collections.abc.ItemsView, (KT, VT_co))
    ValuesView = _pep604(collections.abc.ValuesView, VT_co)
    ContextManager = _pep604(_ContextManager, T_co, name="ContextManager")
    AsyncContextManager = _pep604(_AContextManager, T_co, name="AsyncContextManager")
    Dict = _pep604(dict, (KT, VT), name="Dict")
    DefaultDict = _pep604(collections.defaultdict, (KT, VT), name="DefaultDict")
    OrderedDict = _pep604(collections.OrderedDict, (KT, VT))
    Counter = _pep604(collections.Counter, T)
    ChainMap = _pep604(collections.ChainMap, (KT, VT))
    Generator = _pep604(collections.abc.Generator, (T_co, T_contra, V_co))
    AsyncGenerator = _pep604(collections.abc.AsyncGenerator, (T_co, T_contra))
    Type = _pep604(type, CT_co, name="Type")


elif not typing.TYPE_CHECKING and _PYTHON_VERSION == (3, 9):  # pragma: no cover
    from typing import (
        TypeVar,
        _CallableGenericAlias,
        _CallableType,
        _LiteralGenericAlias,
        _LiteralSpecialForm,
        _SpecialForm,
        _SpecialGenericAlias,
        _TupleType,
        _UnionGenericAlias,
    )

    class _PEP604LiteralGenericAlias(_LiteralGenericAlias, PEP604, _root=True):
        pass

    class _PEP604SpecialGenericAlias(_SpecialGenericAlias, PEP604, _root=True):
        def copy_with(self, params: typing.Any) -> typing.Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    class _PEP604CallableGenericAlias(_CallableGenericAlias, PEP604, _root=True):
        pass

    class _PEP604CallableType(_CallableType, PEP604, _root=True):
        def copy_with(self, params: typing.Any) -> typing.Any:
            return _PEP604CallableGenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    class _PEP604TupleType(_TupleType, PEP604, _root=True):
        def copy_with(self, params: typing.Any) -> typing.Any:
            return PEP604GenericAlias(
                self.__origin__,
                params,
                name=self._name,
                inst=self._inst,
            )

    class _PEP604SpecialForm(_SpecialForm, PEP604, _root=True):
        pass

    class _PEP604LiteralSpecialForm(_LiteralSpecialForm, PEP604, _root=True):
        pass

    class _PEP604UnionGenericAlias(_UnionGenericAlias, PEP604, _root=True):
        def copy_with(self, params: typing.Any) -> typing.Any:
            return Union[params]

    @_PEP604SpecialForm
    @wraps(typing.Any)
    def Any(_self: _PEP604SpecialForm, parameters: typing.Any) -> typing.Any:  # noqa: N802
        return typing.Any[parameters]

    @_PEP604SpecialForm
    @wraps(typing.Union)
    def Union(self: _PEP604SpecialForm, parameters: typing.Any) -> typing.Any:  # noqa: N802
        parameters = tuple(
            parameter.proxied_type if isinstance(parameter, PEP604Proxy) else parameter
            for parameter in parameters
        )
        return _PEP604UnionGenericAlias(self, typing.Union[parameters].__args__)

    @_PEP604SpecialForm
    @wraps(typing.Optional)
    def Optional(self: _PEP604SpecialForm, parameters: typing.Any) -> typing.Any:  # noqa: N802
        return _PEP604UnionGenericAlias(self, typing.Optional[parameters].__args__)

    @_PEP604LiteralSpecialForm
    @wraps(typing.Literal)
    def Literal(self: _PEP604LiteralSpecialForm, *parameters: typing.Any) -> typing.Any:  # noqa: N802
        return _PEP604LiteralGenericAlias(self, typing.Literal[parameters].__args__)

    _pep604 = _PEP604SpecialGenericAlias

    # Default replacements for built-in types.
    Awaitable = _pep604(collections.abc.Awaitable, 1)
    Coroutine = _pep604(collections.abc.Coroutine, 3)
    AsyncIterable = _pep604(collections.abc.AsyncIterable, 1)
    AsyncIterator = _pep604(collections.abc.AsyncIterator, 1)
    Iterable = _pep604(collections.abc.Iterable, 1)
    Iterator = _pep604(collections.abc.Iterator, 1)
    Reversible = _pep604(collections.abc.Reversible, 1)
    Container = _pep604(collections.abc.Container, 1)
    Collection = _pep604(collections.abc.Collection, 1)
    Callable = _PEP604CallableType(collections.abc.Callable, 2)
    AbstractSet = _pep604(collections.abc.Set, 1, name="AbstractSet")
    MutableSet = _pep604(collections.abc.MutableSet, 1)
    Mapping = _pep604(collections.abc.Mapping, 2)
    MutableMapping = _pep604(collections.abc.MutableMapping, 2)
    Sequence = _pep604(collections.abc.Sequence, 1)
    MutableSequence = _pep604(collections.abc.MutableSequence, 1)
    Tuple = _PEP604TupleType(tuple, -1, name="Tuple")
    List = _pep604(list, 1, name="List")
    Deque = _pep604(collections.deque, 1, name="Deque")
    Set = _pep604(set, 1, name="Set")
    FrozenSet = _pep604(frozenset, 1, name="FrozenSet")
    MappingView = _pep604(collections.abc.MappingView, 1)
    KeysView = _pep604(collections.abc.KeysView, 1)
    ItemsView = _pep604(collections.abc.ItemsView, 2)
    ValuesView = _pep604(collections.abc.ValuesView, 1)
    ContextManager = _pep604(_ContextManager, 1, name="ContextManager")
    AsyncContextManager = _pep604(_AContextManager, 1, name="AsyncContextManager")
    Dict = _pep604(dict, 2, name="Dict")
    DefaultDict = _pep604(collections.defaultdict, 2, name="DefaultDict")
    OrderedDict = _pep604(collections.OrderedDict, 2)
    Counter = _pep604(collections.Counter, 1)
    ChainMap = _pep604(collections.ChainMap, 2)
    Generator = _pep604(collections.abc.Generator, 3)
    AsyncGenerator = _pep604(collections.abc.AsyncGenerator, 2)
    Type = _pep604(type, 1, name="Type")


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
        global_registry[old_obj] = PEP604GenericAlias(old_obj, type_vars)
