
# modern_types [![Package version](https://img.shields.io/pypi/v/modern-types?label=PyPI)](https://pypi.org/project/modern-types/) [![Supported Python versions](https://img.shields.io/pypi/pyversions/modern-types.svg?logo=python&label=Python)](https://pypi.org/project/modern-types/)
[![Tests](https://github.com/bswck/modern_types/actions/workflows/test.yml/badge.svg)](https://github.com/bswck/modern_types/actions/workflows/test.yml)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/bswck/modern_types.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/bswck/modern_types)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg?label=Code%20style)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/bswck/modern_types.svg?label=License)](https://github.com/bswck/modern_types/blob/HEAD/LICENSE)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

`__modern_types__` aims to provide [PEP 585](https://peps.python.org/pep-0585/) + [PEP 604](https://peps.python.org/pep-0604/) backports for Python <=3.10 deferred type evaluation backward compatibility.
Hence, the targeted Python versions are 3.8 and 3.9.

# What does it do?
Prevents type errors in evaluating PEP 585 and PEP 604 type annotations for Python 3.8 and 3.9,
which might happen in pydantic models for example.

```py
from __future__ import annotations
from collections import defaultdict
from pprint import pprint
from typing import get_type_hints

import __modern_types__

class Foo:
    a: dict[str, int]
    b: list[int]
    c: set[int]
    d: tuple[int, ...] | None
    e: frozenset[int]
    f: defaultdict[str, int]

pprint(get_type_hints(Foo, globals(), locals()))
```
gives:
```py
{"a": typing.Dict[str, int],
 "b": typing.List[int],
 "c": typing.Set[int],
 "d": typing.Union[typing.Tuple[int, ...], None],
 "e": typing.FrozenSet[int],
 "f": typing.DefaultDict[str, int]}
```

# How to use?
Simply import `__modern_types__` in your code, and it will override the default global namespace of `typing.get_type_hints`.

And now you can use modern types everywhere in your code and the following replacements will be applied without overwriting your parameters:

| Old type | New type | Without `__modern_types__`, works on Python version... | With `__modern_types__`, works on Python version... | Backports PEP |
|:---:|:---:|:---:|:---:|:---:|
| `dict[KT, VT]` | `typing.Dict[str, int]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `list[VT]` | `typing.List[int]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `set[int]` | `typing.Set[int]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `tuple[int, ...]` | `typing.Tuple[int, ...]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `frozenset[int]` | `typing.FrozenSet[int]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `collections.defaultdict[int]` | `typing.DefaultDict[int]` | >=3.9 | >=3.8 | [PEP 585](https://peps.python.org/pep-0585/) |
| `X \| Y` | `typing.Union[X, Y]` | **>=3.10** | >=3.8 | [PEP 604](https://peps.python.org/pep-0604/) |

> [!Note]
> Some optional replacements will also be performed if possible, according to those listed in the [`__modern_types__.ext`](https://github.com/bswck/modern_types/tree/HEAD/__modern_types__/ext.py) source code.

`__modern_types__` additionally makes sure that generic aliases above are instantiable, which isn't the default behavior.

# Use case
Keep your codebase up-to-date by speeding up migrating to modern types, even if you support Python versions >=3.8,<=3.10.
Stop using deprecated `typing.Dict`, `typing.List`, `typing.Set`, `typing.Tuple`, `typing.FrozenSet` and `typing.DefaultDict`!
Importing `__modern_types__` will make all `typing.get_type_hints`-dependent parts of your application, including pydantic models, work with PEP 585 and PEP 604.

# Can `__modern_types__` be used in production?
Yes. It won't break the existing code despite the monkeypatch. The library simply overrides the default global namespace of `typing.get_type_hints` and tries to re-assign name-to-object references of un-subscriptable and un-orable types in relevant modules.
If some keys that `__modern_types__` would supply to `typing.get_type_hints` global namespace are present, they are used instead of the `__modern_types__` ones.

# Installation
If you want to…



## …use this tool in your project 💻
You might simply install it with pip:

```shell
pip install modern-types
```

If you use [Poetry](https://python-poetry.org/), then run:

```shell
poetry add modern-types
```

## …contribute to [modern_types](https://github.com/bswck/modern_types) 🚀

<!--
This section was generated from bswck/skeleton@4089ffe.
Instead of changing this particular file, you might want to alter the template:
https://github.com/bswck/skeleton/tree/4089ffe/fragments/guide.md
-->

> [!Note]
> If you use Windows, it is highly recommended to complete the installation in the way presented below through [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).



1.  Fork the [modern_types repository](https://github.com/bswck/modern_types) on GitHub.

1.  [Install Poetry](https://python-poetry.org/docs/#installation).<br/>
    Poetry is an amazing tool for managing dependencies & virtual environments, building packages and publishing them.
    You might use [pipx](https://github.com/pypa/pipx#readme) to install it globally (recommended):

    ```shell
    pipx install poetry
    ```

    <sub>If you encounter any problems, refer to [the official documentation](https://python-poetry.org/docs/#installation) for the most up-to-date installation instructions.</sub>

    Be sure to have Python 3.8 installed—if you use [pyenv](https://github.com/pyenv/pyenv#readme), simply run:

    ```shell
    pyenv install 3.8
    ```

1.  Clone your fork locally and install dependencies.

    ```shell
    git clone https://github.com/your-username/modern_types path/to/modern_types
    cd path/to/modern_types
    poetry env use $(cat .python-version)
    poetry install
    ```

    Next up, simply activate the virtual environment and install pre-commit hooks:

    ```shell
    poetry shell
    pre-commit install --hook-type pre-commit --hook-type pre-push
    ```

For more information on how to contribute, check out [CONTRIBUTING.md](https://github.com/bswck/modern_types/blob/HEAD/CONTRIBUTING.md).<br/>
Always happy to accept contributions! ❤️


# Legal info
© Copyright by Bartosz Sławecki ([@bswck](https://github.com/bswck)).
<br />This software is licensed under the terms of [MIT License](https://github.com/bswck/modern_types/blob/HEAD/LICENSE).
