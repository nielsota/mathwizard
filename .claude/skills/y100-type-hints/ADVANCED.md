# Advanced Type Hints (Y118-Y127)

Advanced guidelines covering mypy configuration, decorator typing, and abstract base class patterns.

---

## Y118-STRICT-MODE

**Description:** Enable mypy strict mode in your project configuration.

**Rationale:** Strict mode catches more errors, enforces best practices, ensures consistency.

**Configuration:**
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

**What strict mode enables:**
- `--disallow-untyped-defs`: All functions must have type hints
- `--disallow-any-unimported`: Can't use Any from untyped imports
- `--warn-return-any`: Warns when returning Any
- `--warn-redundant-casts`: Catches unnecessary casts
- `--no-implicit-optional`: x: int = None is an error

**Benefits:**
- Forces comprehensive type coverage
- Catches bugs early
- Improves code documentation
- Enables confident refactoring

**Tool Support:** mypy `--strict` flag or `strict = true` in config.

**Related:** Y100-USE-TYPE-HINTS, Y109-AVOID-ANY

---

## Y119-TYPE-COMMENTS

**Description:** Avoid type comments. Use modern annotation syntax instead.

**Rationale:** Type comments are legacy syntax for Python <3.6. Modern annotations are clearer.

**Example:**
```python
# Good - modern annotations (Python 3.6+)
def process(data: list[int]) -> int:
    total: int = 0
    items: list[str] = []
    return total

# Bad - type comments (legacy)
def process(data):
    # type: (list[int]) -> int
    total = 0  # type: int
    items = []  # type: list[str]
    return total
```

**Tool Support:** Modern annotations work in Python 3.6+. Use them exclusively.

**Related:** Y100-USE-TYPE-HINTS

---

## Y120-TYPE-CHECKING

**Description:** Use `if TYPE_CHECKING:` for import-only type hints to avoid circular imports.

**Rationale:** TYPE_CHECKING is False at runtime, allowing imports only needed for type checking.

**Example:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported for type checking, not at runtime
    from parser import TransactionParser  # Circular import OK here

# Use string literal in runtime code
class Processor:
    def __init__(self, parser: "TransactionParser"):
        self.parser = parser

# Or use PEP 563 (Python 3.7+)
from __future__ import annotations

class Processor:
    def __init__(self, parser: TransactionParser):  # Quoted automatically
        self.parser = parser
```

**Tool Support:** TYPE_CHECKING from `typing`. mypy evaluates as True.

**Related:** Y100-USE-TYPE-HINTS, Y121-FORWARD-REFS

---

## Y121-FORWARD-REFS

**Description:** Use forward references (string literals) for types not yet defined or circular dependencies.

**Rationale:** Forward refs allow referencing types before they're defined.

**Example:**
```python
# Good - forward reference
class Node:
    def __init__(self, value: int, parent: "Node | None" = None):
        self.value = value
        self.parent = parent
        self.children: list[Node] = []  # OK after definition

# Good - PEP 563 deferred evaluation (Python 3.7+)
from __future__ import annotations

class Node:
    def __init__(self, value: int, parent: Node | None = None):
        self.value = value
        self.parent = parent
        self.children: list[Node] = []
```

**Tool Support:** String literals or `from __future__ import annotations`.

**Related:** Y120-TYPE-CHECKING, Y100-USE-TYPE-HINTS

---

## Y122-OVERLOAD

**Description:** Use `@overload` for functions with different signatures based on argument types.

**Rationale:** Overloads provide precise type information for different call patterns.

**Example:**
```python
from typing import overload

# Good - overloaded signatures
@overload
def parse(text: str) -> Transaction: ...

@overload
def parse(text: str, strict: Literal[True]) -> Transaction: ...

@overload
def parse(text: str, strict: Literal[False]) -> Transaction | None: ...

def parse(text: str, strict: bool = True) -> Transaction | None:
    """Parse text. If strict=False, returns None on error."""
    try:
        return Transaction.from_string(text)
    except ValueError:
        if strict:
            raise
        return None

# Usage - types are precise
t1: Transaction = parse("100.50")  # Never None (strict=True default)
t2: Transaction | None = parse("invalid", strict=False)  # Might be None

# Bad - imprecise return type (callers must handle None even when strict=True)
def parse(text: str, strict: bool = True) -> Transaction | None:
    ...
```

**Tool Support:** @overload from `typing`. mypy checks signature compatibility.

**Related:** Y107-LITERAL-TYPES, Y110-UNION-TYPES

---

## Y123-PARAMSPEC

**Description:** Use ParamSpec to preserve function signatures in decorators.

**Rationale:** ParamSpec ensures decorators don't lose parameter type information.

**Example:**
```python
from typing import TypeVar, ParamSpec, Callable

P = ParamSpec("P")
R = TypeVar("R")

# Good - preserves signature
def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that preserves exact signature."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def process_transaction(txn: Transaction, validate: bool = True) -> bool:
    """Process a transaction."""
    ...

# Type checking works correctly
process_transaction(txn, validate=False)  # OK
process_transaction(txn, invalid=True)     # mypy error

# Bad - loses signature
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

**Tool Support:** ParamSpec from `typing` (Python 3.10+) or `typing_extensions`.

**Related:** Y113-CALLABLE-TYPES, Y311-DECORATOR-PATTERN

---

## Y124-CONCATENATE

**Description:** Use Concatenate to add parameters to callables (useful for method decorators).

**Rationale:** Concatenate allows prepending parameters to Callable types, enabling precise typing of method decorators.

**Example:**
```python
from typing import TypeVar, ParamSpec, Callable, Concatenate

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

# Good - method decorator with Concatenate
def log_method(func: Callable[Concatenate[T, P], R]) -> Callable[Concatenate[T, P], R]:
    """Decorator for methods that logs self."""
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Method called on {self}")
        return func(self, *args, **kwargs)
    return wrapper

class Processor:
    @log_method
    def process(self, txn: Transaction, validate: bool = True) -> bool:
        """Process transaction."""
        ...

# Type checking preserved
proc = Processor()
proc.process(txn, validate=False)  # OK
```

**Tool Support:** Concatenate from `typing` (Python 3.10+) or `typing_extensions`.

**Related:** Y123-PARAMSPEC, Y311-DECORATOR-PATTERN

---

## Y125-ENFORCE-IMMUTABILITY-VIA-TYPES

**Description:** Enforce immutability through type hints (e.g., `Sequence`, `Mapping`, `AbstractSet`) rather than creating immutable copies of collections.

**Rationale:** Type hints provide compile-time immutability guarantees without runtime overhead.

**Example:**
```python
from collections.abc import Sequence, Mapping
from collections.abc import Set as AbstractSet

# Good - immutability enforced via type hint
def get_categories() -> Sequence[str]:
    """Returns immutable view of categories."""
    categories = ["Food", "Transport", "Entertainment"]
    return categories  # Returns mutable list, but type says immutable

# Callers cannot modify (enforced by mypy)
cats = get_categories()
# cats.append("New")  # mypy error: Sequence has no append method

# Good - immutable mapping
def get_config() -> Mapping[str, int]:
    config = {"timeout": 30, "retries": 3}
    return config

# Bad - unnecessary runtime overhead
def get_categories() -> tuple[str, ...]:
    categories = ["Food", "Transport", "Entertainment"]
    return tuple(categories)  # Runtime cost!
```

**When to use:**
- Return types: `Sequence[T]` instead of `list[T]` when callers shouldn't modify
- Return types: `Mapping[K, V]` instead of `dict[K, V]` when callers shouldn't modify
- Return types: `AbstractSet[T]` instead of `set[T]` when callers shouldn't modify

**Import Note:** Use `from collections.abc import Set as AbstractSet` to avoid conflicts with built-in `set`.

**Tool Support:** mypy enforces method availability based on type.

**Related:** Y101-PRECISE-TYPES, Y106-COLLECTION-TYPES, Y400-IMMUTABILITY

---

## Y126-USE-METACLASS-ABCMETA

**Description:** When using abstract base classes, use `metaclass=ABCMeta` with `@abstractmethod` decorator and ellipsis body.

**Rationale:**
- `metaclass=ABCMeta` keeps MRO simpler than inheriting from `ABC`
- `@abstractmethod` provides compile-time checking
- Ellipsis (`...`) is the modern way to indicate "no implementation"

**Example:**
```python
from abc import ABCMeta, abstractmethod
from typing import Any, Self

# Good - metaclass pattern with abstractmethod and ellipsis
class Asset(metaclass=ABCMeta):
    @abstractmethod
    def create_performance(self, context: MarketContext) -> AssetPerformance:
        """Create performance data for this asset."""
        ...

    @property
    @abstractmethod
    def asset_id(self) -> str:
        """Unique identifier for this asset."""
        ...

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict[str, Any]) -> Self:
        """Create asset from configuration."""
        ...

# Bad - using NotImplementedError instead of @abstractmethod
class Asset:
    def create_performance(self, context: MarketContext) -> AssetPerformance:
        raise NotImplementedError("Subclasses must implement")

# Bad - inheriting from ABC (ABC now in MRO)
from abc import ABC
class Asset(ABC): ...

# Bad - using pass instead of ellipsis
class Asset(metaclass=ABCMeta):
    @abstractmethod
    def create_performance(self, context: MarketContext) -> AssetPerformance:
        pass  # Use ... instead
```

**Tool Support:** mypy enforces `@abstractmethod` at type-check time. Python raises `TypeError` if abstract class is instantiated.

**Related:** Y102-USE-PROTOCOLS, Y117-SELF-TYPE, Y127-DEFINE-CONTRACTS-IN-CODE

---

## Y127-DEFINE-CONTRACTS-IN-CODE

**Description:** Define contracts explicitly in code (class attributes with `__init__` methods, abstract properties) instead of documenting them in docstrings.

**Rationale:** Code-based contracts are enforced by type checkers and provide better IDE support. Documentation-only contracts require `# type: ignore` comments.

**Example:**
```python
from abc import ABCMeta, abstractmethod

# Good - attributes declared AND initialized
class Asset(metaclass=ABCMeta):
    """Abstract base class for financial assets."""

    # Required attributes declared for type checking
    id: str
    name: str

    def __init__(self, id: str, name: str) -> None:
        """Initialize required attributes."""
        self.id = id
        self.name = name

    @classmethod
    @abstractmethod
    def get_performance_type(cls) -> type[AssetPerformance]:
        ...

# Usage - no type: ignore needed
def process_assets(assets: list[Asset]) -> None:
    for asset in assets:
        print(asset.id, asset.name)  # Type checker knows these exist

# Bad - only documented, not defined (requires type: ignore)
class Asset(metaclass=ABCMeta):
    """
    Subclass Contract:
    - Must define `id: str` attribute
    - Must define `name: str` attribute
    """
    ...
```

**Good patterns:**
- Declare attributes at class level: `id: str`
- Provide `__init__` method that initializes them
- Abstract properties for computed values
- Type stubs (`.pyi` files) for third-party libraries

**Tool Support:** mypy catches missing attributes in subclasses.

**Related:** Y100-USE-TYPE-HINTS, Y102-USE-PROTOCOLS, Z202-IGNORING-TYPE-ERRORS
