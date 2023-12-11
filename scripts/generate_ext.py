#!/usr/bin/env python3

"""Generate `ext.py` from typeshed. Python 3.9+ required."""

from __future__ import annotations

import ast
import re
import string
import subprocess
import sys
from contextvars import ContextVar, copy_context
from functools import partial
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path

PATTERN: re.Pattern[str] = re.compile(
    "class ([A-Z][A-Za-z0-9_]*)\\(.*Generic\\[(.*)\\]\\.*\\):",
)

TYPE_PARAM_PATTERN: re.Pattern[str] = re.compile(
    "TypeVar\\(\\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\\s*(?:, )?(.*)\\)"
)

EXT_TEMPLATE = string.Template(
    """\"""
Auto-patch generic classes from typeshed.

Generated by `modern_types/scripts/generate_ext.py`.
\"""

from __future__ import annotations

${imports}

from __modern_types__ import patch

${type_variables}

${stdlib_patches}

${third_party_patches}"""
)

TYPESHED = Path("typeshed/")
TYPESHED_STDLIB = TYPESHED / "stdlib"
TYPESHED_THIRD_PARTY = TYPESHED / "stubs"
STUB_SUFFIX = ".pyi"

ANY_USED = ContextVar("ANY_USED", default=False)


@dataclass(frozen=True)
class ModuleInfo:
    name: str
    path: Path
    root: str
    source_code: str
    type_vars: set[TypeParam]


@dataclass(frozen=True)
class Location:
    module_info: ModuleInfo
    match: re.Match[str]

    def __str__(self) -> str:
        line_no = sum(
            1 for _ in self.module_info.source_code[: self.match.span()[0]].split("\n")
        )
        return str(self.module_info.path) + ":" + str(line_no)


@dataclass(frozen=True)
class GenericSignature:
    class_name: str
    type_parameters: list[TypeParameter]
    location: Location

    @property
    def param_string(self) -> str:
        return ", ".join(map(str, self.type_parameters))

    @property
    def param_tuple_string(self) -> str:
        param_string = self.param_string
        if len(self.type_parameters) == 1:
            param_string += ","
        return param_string.join("()")

    @property
    def ref(self) -> str:
        return f"{self.location.module_info.name}.{self.class_name}"

    @property
    def where(self) -> str:
        return str(self.location)

    @property
    def patch_call(self) -> str:
        return (
            f"# Generated from `{self.location.match.group(0)}`\n"
            f'# @ {self.where}\npatch("{self.ref}", '
            f"{self.param_tuple_string})\n"
        )

    def __str__(self) -> str:
        return f"{self.class_name}({self.param_string}) ({self.location})"


class DoubleQuoteName(str):
    def __repr__(self) -> str:
        return f'"{self}"'


@dataclass(order=True, unsafe_hash=True, frozen=True)
class TypeVarInfo:
    name: str = field(compare=True)
    location: Location = field(compare=False, hash=False)

    @property
    def assign_stmt(self) -> str:
        orig_expr = self.location.match.group(0)
        call: ast.Call = ast.parse(orig_expr).body[0].value
        call.args[0].value = DoubleQuoteName(call.args[0].value)
        comment = preceding_comment = ""
        for keyword in call.keywords:
            if (
                keyword.arg == "covariant"
                and not self.name.endswith("_co")
                or keyword.arg == "contravariant"
                and not self.name.endswith("_contra")
            ):
                comment = "# noqa: PLC0105"
        if call.args[1:]:
            call.args = call.args[:1]
            for keyword in call.keywords:
                if keyword.arg == "bound":
                    call.keywords.remove(keyword)
            call.keywords.append(
                ast.keyword(arg="bound", value=ast.Name(id="Any", ctx=ast.Load()))
            )
        else:
            for keyword in call.keywords:
                if keyword.arg == "bound":
                    keyword.value = ast.Name(id="Any", ctx=ast.Load())
        expr = ast.unparse(call)
        differs = orig_expr != expr
        ANY_USED.set(ANY_USED.get() or differs)
        preceding_comment = f"# Generated from `{orig_expr}`\n" f"# @ {self.location}\n"
        if comment:
            comment = "  " + comment
        return (preceding_comment + f"{self.name} = {expr}" + comment).strip()


def find_generic_signatures(module_path: Path, *, root: str = "stdlib") -> None:
    source_code = module_path.read_text()
    module_name = (
        str(module_path)
        .removeprefix(str(TYPESHED / Path(root)))
        .removesuffix(STUB_SUFFIX)
        .replace("/", ".")
        .removeprefix(".")
    )
    type_vars = []
    module_info = ModuleInfo(
        path=module_path,
        name=module_name,
        root=root,
        source_code=source_code,
        type_vars=type_vars,
    )
    type_vars.extend(
        TypeVarInfo(
            name=match.group(1),
            location=Location(
                module_info=module_info,
                match=match,
            ),
        )
        for match in TYPE_PARAM_PATTERN.finditer(source_code)
    )
    for match in PATTERN.finditer(source_code):
        yield GenericSignature(
            location=Location(
                module_info=module_info,
                match=match,
            ),
            class_name=match.group(1),
            type_parameters=[*map(str.strip, match.group(2).split(","))],
        )


def find_generics(path: Path = Path("."), root: str = "stdlib") -> None:
    if root == "stubs/*":
        root_dir = "stubs"
        root = "stubs"
    else:
        root_dir = root
    for module_path in (TYPESHED / root_dir / path).glob("**/*" + STUB_SUFFIX):
        if not module_path.is_dir():
            yield from find_generic_signatures(
                module_path,
                root=root.replace("*", module_path.parts[0]),
            )


def generate_ext_script(path: Path[str] = Path("__modern_types__/ext.py")) -> None:
    type_vars = []

    def collect_type_vars(generic: GenericSignature) -> set[TypeVarInfo]:
        type_vars.extend(
            type_var
            for type_var in generic.location.module_info.type_vars
            if type_var.name in ("AnyStr", *generic.type_parameters)
        )
        return generic

    path.write_text(
        EXT_TEMPLATE.substitute(
            stdlib_patches="\n".join(
                generic.patch_call
                for generic in map(collect_type_vars, find_generics(root="stdlib"))
            ),
            third_party_patches="\n".join(
                generic.patch_call
                for generic in map(collect_type_vars, find_generics(root="stubs/*"))
            ),
            type_variables="\n".join(
                f"{type_var.assign_stmt}\n"
                for type_var in sorted(set(chain(type_vars)))
            ),
            imports="\n".join(
                (f"from typing import {'Any, ' if ANY_USED.get() else ''}TypeVar",)
            ),
        )
    )


if __name__ == "__main__":
    copy_context().run(generate_ext_script)
