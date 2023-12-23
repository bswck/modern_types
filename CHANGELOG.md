# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).<br/>
This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->

## [v2.0.6](https://github.com/bswck/modern_types/tree/v2.0.6) (2023-12-23)


### Changed

- * Exported `PEP604GenericAliasLink` in `__modern_types__/__init__.py`.
  * Corrected the README.

### Fixed

- Python version information in the README.
- `register()` breaking behavior on Python 3.8.


## [v2.0.5](https://github.com/bswck/modern_types/tree/v2.0.5) (2023-12-23)


No significant changes.


## [v2.0.4](https://github.com/bswck/modern_types/tree/v2.0.4) (2023-12-15)


### Fixed

- Moved flattening activation from tests to the main codebase.


## [v2.0.3](https://github.com/bswck/modern_types/tree/v2.0.3) (2023-12-15)


### Fixed

- Handling corner cases, such as when an external module is involved in the AST expression or non-generic types need unions.


## [v2.0.2](https://github.com/bswck/modern_types/tree/v2.0.2) (2023-12-12)


### Changed

- Once a type replacement is registered with `register()`, it must be manually removed from the registry to be changed by `register()`.


## [v2.0.1](https://github.com/bswck/modern_types/tree/v2.0.1) (2023-12-11)


No significant changes.


## [v2.0.0](https://github.com/bswck/modern_types/tree/v2.0.0) (2023-12-11)


### Fixed

- Rewrote the lib to use AST for overwriting namespaces, stopped mutating developer-end namespaces.


## [v1.0.8](https://github.com/bswck/modern_types/tree/v1.0.8) (2023-12-11)


### Fixed

- `recursive_guard` was added in 3.9.


## [v1.0.7](https://github.com/bswck/modern_types/tree/v1.0.7) (2023-12-11)


### Fixed

- Now works with [pydantic](https://pydantic.dev) which doesn't use `typing.get_type_hints`, but its own version that calls `typing._eval_type`.


## [v1.0.6](https://github.com/bswck/modern_types/tree/v1.0.6) (2023-12-11)


### Fixed

- `collections.defaultdict[int, str] | None` was impossible, because it was a 3.9 `types.GenericAlias` without `X | Y` union type syntax support.


## [v1.0.5](https://github.com/bswck/modern_types/tree/v1.0.5) (2023-12-11)


### Changed

- Significant README and docstring improvements.


## [v1.0.4](https://github.com/bswck/modern_types/tree/v1.0.4) (2023-12-11)


### Fixed

- Documentation.


## [v1.0.3](https://github.com/bswck/modern_types/tree/v1.0.3) (2023-12-11)


### Changed

- Enriched the README.


## [v1.0.2](https://github.com/bswck/modern_types/tree/v1.0.2) (2023-12-11)


### Added

- Some more description in the README.


## [v1.0.1](https://github.com/bswck/modern_types/tree/v1.0.1) (2023-12-11)


### Fixed

- `scripts/generate_auto.py` was mistakenly generating `__modern_types__/auto.py` instead of `__modern_types__/_auto.py`.


## [v1.0.0](https://github.com/bswck/modern_types/tree/v1.0.0) (2023-12-11)


### Added

- Full tests and implementation. ([#43283077](https://github.com/bswck/modern_types/issues/43283077))
