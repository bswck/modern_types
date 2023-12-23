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
from functools import wraps
from types import SimpleNamespace

from __modern_types__._registry import (
    PEP604Link,
    PEP604Proxy,
    create_dest_alias,
    global_registry,
    register,
)

__all__ = (
    "TypeHintVisitor",
    "register",
    "registry",
)


_PYTHON_VERSION = sys.version_info[:2]  # without PATCH version
_WARNING_3_10 = "You do not need to import __modern_types__ on Python >=3.10."

# ruff: noqa: N802


class _Bunch(SimpleNamespace):
    def __getitem__(self, key: str) -> object:
        return getattr(self, key)

    def __setitem__(self, key: str, value: object) -> None:
        setattr(self, key, value)


class TypeHintVisitor(ast.NodeTransformer):
    """
    Type hint visitor.

    Example.
    --------
    >>> import collections.abc
    >>> from __modern_types__ import TypeHintVisitor
    ...
    >>> global_ns = {"collections": collections}
    >>> local_ns = {}
    >>> visitor = TypeHintVisitor(global_ns, local_ns)
    >>> visitor.visit(ast.parse("a: collections.abc.Mapping[str, int]"))
    <_ast.Module object at 0x7f9b1c0b6d30>
    >>> local_ns
    {'a': typing.Mapping[str, int]}
    """

    registry: dict[object, object]

    def __init__(
        self,
        global_ns: dict[str, object],
        local_ns: dict[str, object],
        builtin_ns: dict[str, object] | None = None,
        registry: dict[object, object] | None = None,
    ) -> None:
        """Initialize TypeHintVisitor."""
        if builtin_ns is None:
            builtin_ns = vars(builtins)
        if registry is None:
            registry = global_registry
        self.registry = registry
        self.local_ns = local_ns
        self.global_ns = global_ns
        self.builtin_ns = builtin_ns

    @property
    def lookup(self) -> dict[str, object]:
        """Return a lookup dict for all namespaces."""
        return {**self.builtin_ns, **self.global_ns, **self.local_ns}

    def set_backport_for(  # noqa: C901, PLR0912
        self,
        path: list[str],
        obj: object | None = None,
        *,
        pep604: bool = False,
        pep604_name: str | None = None,
    ) -> None:
        """
        Set a backport object for an object at a given attribute path.

        Example.
        --------
        >>> import collections.abc
        >>> from __modern_types__ import TypeHintBackportSetter
        ...
        >>> backports = TypeHintBackportSetter({"collections": collections}, {}).
        >>> backports.set_backport_for(["collections", "abc", "Mapping"])
        >>> backports.global_ns["collections"].abc.Mapping
        typing.Mapping[~KT, ~VT_co]
        """
        if not path:
            return

        init_path = path[0]
        write_ns = None

        if init_path in self.local_ns:
            write_ns = self.local_ns
        elif init_path in self.global_ns or init_path in self.builtin_ns:
            write_ns = self.global_ns

        if write_ns is None:
            msg = f"namespace of {init_path!r} not found"
            raise LookupError(msg)

        current_ns: dict[str, object] | _Bunch = write_ns

        if len(path) > 1:
            *path_to, path_end = path[1:]

            try:
                ns = current_ns[init_path]
            except KeyError:
                return

            if not isinstance(ns, _Bunch):
                current_ns[init_path] = current_ns = _Bunch(**vars(ns))

            for name in path_to:
                next_ns = current_ns[name]
                if not isinstance(next_ns, _Bunch):
                    next_ns = current_ns[name] = _Bunch(**vars(next_ns))
                current_ns = next_ns
        else:
            path_end = init_path

        if obj is None:
            try:
                obj = current_ns[path_end]
            except KeyError:
                if len(path) == 1:
                    obj = self.builtin_ns[path_end]
                else:
                    raise

        if obj in self.registry:
            obj = self.registry[obj]

        if pep604 and not isinstance(obj, PEP604Link):
            obj = PEP604Proxy(
                obj,
                path_end,
                path_end := pep604_name or path_end,
            )

        current_ns[path_end] = obj

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """Visit an attribute node. Note the behavior for children is different."""
        attr_path: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                attr_path.insert(0, child.id)
            elif isinstance(child, ast.Attribute):
                attr_path.insert(0, child.attr)
            elif not isinstance(child, ast.Load):
                return node
        self.set_backport_for(attr_path)
        return node

    def visit_Name(self, node: ast.Name, *, pep604: bool = False) -> ast.Name:
        """Visit a name node. Can replace it with a backport."""
        if pep604:
            pep604_name = node.id
            while pep604_name in self.lookup:
                pep604_name += "__pep604"
            self.set_backport_for(
                [node.id],
                pep604=pep604,
                pep604_name=pep604_name,
            )
            if pep604_name in self.lookup:
                return ast.Name(id=pep604_name, ctx=node.ctx)
            return node
        self.set_backport_for([node.id])
        return node

    def pep604_visit(self, node: ast.AST) -> ast.AST:
        """Visit a node and replace it with a backport if needed."""
        if isinstance(node, ast.Name):
            return self.visit_Name(node, pep604=True)
        self.visit(node)
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        """Visit a binary operation node. Used for PEP 604 detection."""
        if isinstance(node.op, ast.BitOr):
            node.left = self.pep604_visit(node.left) or node.left  # type: ignore[assignment]
            self.visit(node.op)
            node.right = self.pep604_visit(node.right) or node.right  # type: ignore[assignment]
        else:
            self.generic_visit(node)
        return node


if _PYTHON_VERSION < (3, 10):
    _builtin_evaluate = typing.ForwardRef._evaluate  # noqa: SLF001

    @wraps(_builtin_evaluate)
    def _wrap_evaluate(
        self: typing.ForwardRef,
        globalns: dict[str, object] | None = None,
        localns: dict[str, object] | None = None,
        recursive_guard: frozenset[str] | None = None,
    ) -> typing.Any:
        """PEP 585 & PEP 604 backport."""
        # Copy the namespaces to avoid mutating them by TypeHintVisitor
        globalns = (globalns or {}).copy()
        localns = (localns or {}).copy()

        # The type hint to evaluate
        hint = ast.parse(self.__forward_arg__, mode="eval")

        # Perform the magic settings in globalns and localns
        TypeHintVisitor(globalns, localns).visit(hint)

        ast.fix_missing_locations(hint)

        self.__forward_code__ = compile(hint, filename="<type hint>", mode="eval")

        # Call the original _evaluate
        return create_dest_alias(
            _builtin_evaluate(
                self,
                globalns,
                localns,
                *() if _PYTHON_VERSION == (3, 8) else (recursive_guard or frozenset(),),
            ),
        )

    typing.ForwardRef._evaluate = typing.cast(typing.Any, _wrap_evaluate)  # type: ignore[attr-defined,method-assign,unused-ignore] #  noqa: SLF001

    from __modern_types__._typeshed import register_typeshed_generics

    register_typeshed_generics()
else:
    import warnings

    warnings.warn(_WARNING_3_10, category=DeprecationWarning, stacklevel=-1)
