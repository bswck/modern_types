"""
`__modern_types__`.

`__modern_types__` aims to provide [PEP 585](https://peps.python.org/pep-0585/)
+ [PEP 604](https://peps.python.org/pep-0604/) backports for Python <=3.10
deferred type evaluation backward compatibility.

(C) 2023-present Bartosz Sławecki (bswck)
"""
from __future__ import annotations

import ast
import builtins
import sys
import typing

from __modern_types__._registry import register, registry

__all__ = (
    "register",
    "registry",
)


_PYTHON_VERSION = sys.version_info[:2]  # without PATCH version
_WARNING_3_10 = "You do not need to import __modern_types__ on Python >=3.10."

if _PYTHON_VERSION < (3, 10):
    _builtin_evaluate = typing.ForwardRef._evaluate  # noqa: SLF001

    def _wrap_evaluate(
        self: typing.ForwardRef,
        globalns: dict[str, typing.Any] | None = None,
        localns: dict[str, typing.Any] | None = None,
        recursive_guard: typing.Any = None,
    ) -> typing.Any:
        """PEP 585 & PEP 604 backport."""
        tree = ast.parse(self.__forward_arg__, mode="eval")

        # Copy the namespaces to ensure we don't modify the caller's namespaces.
        globalns = (globalns or {}).copy()
        localns = (localns or {}).copy()
        builtin_ns = vars(builtins)
        missing = object()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                name = node.id
                scope = localns
                cls = localns.get(name, missing)
                if cls is missing:
                    cls = globalns.get(name, missing)
                    scope = globalns
                if cls is missing:
                    cls = builtin_ns.get(name, missing)
                if cls is missing:
                    continue  # this will be a NameError, skip
                replacement = registry.get(cls, missing)
                if replacement is missing:
                    continue  # not a registered type, skip
                scope[name] = replacement
        return _builtin_evaluate(
            self,
            globalns,
            localns,
            *(() if _PYTHON_VERSION == (3, 8) else (recursive_guard,)),
        )

    typing.ForwardRef._evaluate = typing.cast(typing.Any, _wrap_evaluate)  # type: ignore[attr-defined,method-assign,unused-ignore] #  noqa: SLF001

    # Automatically patch other modules
    import __modern_types__._typeshed  # noqa: F401
else:
    import warnings

    warnings.warn(_WARNING_3_10, category=DeprecationWarning, stacklevel=-1)
