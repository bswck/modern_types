"""Extra patching utilities for __modern_types__."""

from __future__ import annotations

import inspect
import sys
from contextvars import ContextVar
from typing import _GenericAlias  # type: ignore[attr-defined]

PATCH_STACK_OFFSET = ContextVar("PATCH_STACK_OFFSET", default=1)


def patch(
    ref: str,
    type_vars: object | tuple[object, ...],
    stack_offset: int | None = None,
    *,
    noop_ok: bool = False,
) -> None:
    """Patch a generic class with the __modern_types__ backports."""
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

    alias = _GenericAlias(old_obj, type_vars)
    setattr(module, name, alias)

    if stack_offset is None:
        stack_offset = PATCH_STACK_OFFSET.get()
    frame = inspect.stack()[stack_offset].frame

    importer = sys.modules[frame.f_globals["__name__"]]
    for key, val in vars(importer).items():
        if val is old_obj:
            setattr(importer, key, alias)
