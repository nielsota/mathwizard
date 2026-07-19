---
name: y100-type-hints
description: Python type hints and type safety guidelines (Y100-Y127). Use when writing typed Python code, creating protocols, using generics, defining type aliases, reviewing type annotations, or configuring mypy.
---

# Type Hints & Type Safety (Y100-Y127)

Comprehensive guidelines for Python type hints covering fundamentals, patterns, and advanced usage.

## Quick Reference

| Guideline Range | Topic | Reference File |
|-----------------|-------|----------------|
| Y100-Y109 | Fundamentals (hints, protocols, generics, collections) | [FUNDAMENTALS.md](FUNDAMENTALS.md) |
| Y110-Y117 | Patterns (unions, narrowing, dataclasses, Self) | [PATTERNS.md](PATTERNS.md) |
| Y118-Y127 | Advanced (mypy config, overload, ParamSpec) | [ADVANCED.md](ADVANCED.md) |

## Key Principles

1. **Always use type hints** for function parameters, return values, and class attributes (Y100)
2. **Be precise** - use `Sequence[str]` over `list`, `Mapping` over `dict` (Y101)
3. **Prefer Protocol** over ABC for structural subtyping (Y102)
4. **Avoid Any** - use generics, unions, or protocols instead (Y109)
5. **Enable mypy strict mode** in your project (Y118)

## Most Common Guidelines

### Y100-USE-TYPE-HINTS
Always use type hints for function parameters, return values, and class attributes.

```python
# Good
def parse_transaction(line: str, date_format: str = "%Y-%m-%d") -> Transaction:
    ...

# Bad - no type hints
def parse_transaction(line, date_format="%Y-%m-%d"):
    ...
```

### Y102-USE-PROTOCOLS
Prefer Protocol over ABC for structural subtyping (duck typing with type safety).

```python
from typing import Protocol

class Parser(Protocol[T]):
    def parse(self, text: str) -> T: ...

class VisaParser:  # No inheritance needed
    def parse(self, text: str) -> list[Transaction]: ...
```

### Y109-AVOID-ANY
Avoid `Any` - use generics, unions, or protocols instead.

```python
# Good - generic preserves type
def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# Bad - loses type information
def first(items: Sequence[Any]) -> Any:
    return items[0] if items else None
```

## Detailed Guidelines

For complete guidelines with examples:

- **Fundamentals** (Y100-Y109): See [FUNDAMENTALS.md](FUNDAMENTALS.md)
  - Type hints basics, precise types, protocols, generics
  - Type aliases, NewType, collection types, literals, Final, avoid Any

- **Patterns** (Y110-Y117): See [PATTERNS.md](PATTERNS.md)
  - Union types, type narrowing, dataclass types
  - Callable types, NamedTuple, return hints, ClassVar, Self

- **Advanced** (Y118-Y127): See [ADVANCED.md](ADVANCED.md)
  - mypy strict mode, TYPE_CHECKING, forward refs
  - @overload, ParamSpec, Concatenate, immutability via types
  - ABCMeta patterns, contracts in code

## Tool Support

- **mypy**: Static type checker - `mypy --strict`
- **ruff**: Fast linter with ANN rules for annotations
- **pyright**: Alternative type checker (VS Code Pylance)

## Related Skills

- `z200-type-safety-violations` - Anti-patterns to avoid
- `y112-dataclass-types` - See PATTERNS.md for dataclass guidelines
