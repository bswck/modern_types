"""
__modern_types__.

PEP 585 + PEP 604 backports, because it started becoming annoying.

(C) 2023-present Bartosz Sławecki (bswck)
"""
from __future__ import annotations

import builtins
from builtins import object as _object
from operator import attrgetter
from typing import TYPE_CHECKING, Union, _GenericAlias

if TYPE_CHECKING:
    from typing import Any


class ModernGenericAlias(_GenericAlias, _root=True):
    """A generic alias object."""

    def __repr__(self) -> str:
        """Return a string representation."""
        args = ", ".join(map(attrgetter("__name__"), self.__args__))
        return f"{self.__origin__.__name__}[{args}]"

    def __or__(self, other: Any) -> Any:
        """Return a new union type object."""
        return Union[self, other]


class ModernType(type):
    """Implement PEP 585 and PEP 604."""

    @property
    def __class__(cls) -> type[Any]:
        """Return the original class."""
        return cls.__orig_cls__

    @property
    def __call__(cls) -> Any:
        """Return the original class."""
        return cls.__orig_cls__

    def __instancecheck__(cls, inst: type[Any]) -> bool:
        """Return the original instance check."""
        return isinstance(
            inst,
            cls.__orig_cls__,
        ) or super().__subclasscheck__(inst)

    def __subclasscheck__(cls, subclass: type[Any]) -> bool:
        """Return the original subclass check."""
        return issubclass(
            subclass,
            cls.__orig_cls__,
        ) or super().__subclasscheck__(subclass)

    def __getattribute__(cls, name: str) -> Any:
        """Return the original attribute."""
        _getattr = _object.__getattribute__
        orig_cls = _getattr(cls, "__orig_cls__")
        if name == "__orig_cls__":
            return orig_cls
        obj = _getattr(orig_cls, name)
        get = getattr(obj, "__get__", None)
        if callable(get):
            return get(None, orig_cls)
        return obj

    def __getitem__(cls, params: Any) -> Any:
        """Return a new generic alias object."""
        return ModernGenericAlias(cls.__orig_cls__, params)

    def __or__(cls, other: Any) -> Any:
        """Return a new union type object."""
        return Union[cls.__orig_cls__, other]


_PATCH_BUILTINS = {
    obj
    for obj_name, obj in vars(builtins).items()
    if isinstance(obj, type) and obj_name.isalpha() and obj_name.islower()
} - {super}
_IGNORE_ATTRS = {"__abstractmethods__"}


def _modern_builtin_type(cls: type[Any]) -> None:
    """Create a new modern built-in type."""
    return type(
        cls.__name__,
        (ModernType,),
        {
            **{name: getattr(cls, name) for name in set(dir(cls)) - _IGNORE_ATTRS},
            "__orig_cls__": cls,
        },
    )


def _monkeypatch_modules() -> None:
    from sys import modules
    from types import ModuleType

    class ModernTypeModule(ModuleType):
        def __setattr__(self, name: str, value: Any) -> None:
            if isinstance(value, type):
                value.__bases__ = (*dict.fromkeys((*value.__bases__, ModernType)),)
            super().__setattr__(name, value)

        @classmethod
        def _from_module(cls, module: ModuleType) -> ModernTypeModule:
            inst = cls(module.__name__, module.__doc__)
            inst.__dict__.update(module.__dict__)
            return inst

    modules.update(
        {
            module_name: ModernTypeModule._from_module(module)  # noqa: SLF001
            for module_name, module in modules.items()
        },
    )


def _new_builtins() -> dict[str, object]:
    return {cls.__name__: _modern_builtin_type(cls) for cls in _PATCH_BUILTINS}


if __import__("sys").version_info <= (3, 10):
    vars(__import__("builtins")).update(_new_builtins())
