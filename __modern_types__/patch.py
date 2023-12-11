"""Extra patching utilities for __modern_types__."""

from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING, _GenericAlias

if TYPE_CHECKING:
    from typing import TypeVar


def patch(
    ref: str,
    type_vars: list[TypeVar],
    stack_offset: int = 1,
    *,
    unimported_cancel: bool = True,
) -> None:
    """Patch stdlib generic class with the __modern_types__ backport."""
    module_name, name = ref.partition(".")[::2]
    try:
        module = sys.modules[module_name]
    except KeyError:
        if unimported_cancel:
            return
        msg = f"Module {module_name} must be imported before __modern_types__ patching"
        raise ValueError(msg) from None
    old_obj = getattr(module, name)
    alias = _GenericAlias(old_obj, type_vars)
    setattr(module, name, alias)
    frame = inspect.stack()[stack_offset].frame
    importer = sys.modules[frame.f_globals["__name__"]]
    for key, val in vars(importer).items():
        if val is old_obj:
            setattr(importer, key, alias)
