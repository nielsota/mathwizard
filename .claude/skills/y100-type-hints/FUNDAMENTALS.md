# Type Hints Fundamentals (Y100-Y109)

Core guidelines for Python type hints covering basics, protocols, generics, and collections.

---

## Y100-USE-TYPE-HINTS

**Description:** Always use type hints for function parameters, return values, and class attributes.

**Rationale:** Type hints improve code clarity, enable static analysis, catch bugs early, and serve as documentation.

**Example:**
```python
# Good
def parse_transaction(line: str, date_format: str = "%Y-%m-%d") -> Transaction:
    """Parse a transaction line into a Transaction object."""
    ...

# Bad
def parse_transaction(line, date_format="%Y-%m-%d"):
    """Parse a transaction line into a Transaction object."""
    ...
```

**Tool Support:** mypy strict mode requires type hints. ruff rule ANN enforces annotations.

**Related:** Y101-PRECISE-TYPES, Z207-MISSING-PARAMETER-TYPES

---

## Y101-PRECISE-TYPES

**Description:** Use the most specific type possible. Prefer `Sequence[str]` over `list`, `Mapping[str, int]` over `dict`.

**Rationale:** Precise types communicate intent, enable better type checking, and document constraints.

**Example:**
```python
from collections.abc import Sequence, Mapping

# Good - specific and flexible
def process_names(names: Sequence[str]) -> list[str]:
    """Process names, accepting any sequence type."""
    return [name.upper() for name in names]

# Bad - too specific, limits caller
def process_names(names: list[str]) -> list[str]:
    return [name.upper() for name in names]

# Good - precise return type
def get_config() -> Mapping[str, str]:
    """Returns immutable mapping."""
    return {"host": "localhost"}

# Bad - suggests mutability
def get_config() -> dict[str, str]:
    return {"host": "localhost"}
```

**Tool Support:** mypy detects type mismatches. Use `from collections.abc import Sequence, Mapping, Iterable`.

**Related:** Y102-USE-PROTOCOLS, Y106-COLLECTION-TYPES

---

## Y102-USE-PROTOCOLS

**Description:** Prefer Protocol over ABC for structural subtyping. Use ABC only when inheritance is semantically important.

**Rationale:** Protocols enable duck typing with type safety. They're more flexible than ABCs and don't require explicit inheritance.

**Example:**
```python
from typing import Protocol

# Good - structural subtyping
class Parser(Protocol[T]):
    """Protocol for any parser."""
    def parse(self, text: str) -> T:
        ...

class VisaParser:
    """Concrete parser - no inheritance needed."""
    def parse(self, text: str) -> list[Transaction]:
        ...

# Good - works due to structural compatibility
def run_parser(parser: Parser[T], text: str) -> T:
    return parser.parse(text)

# Bad - requires inheritance
from abc import ABC, abstractmethod

class ParserABC(ABC):
    @abstractmethod
    def parse(self, text: str) -> Any:
        ...

class VisaParser(ParserABC):  # Forced inheritance
    def parse(self, text: str) -> list[Transaction]:
        ...
```

**Tool Support:** mypy supports Protocol from `typing`. Python 3.8+.

**Related:** Y201-INTERFACE-SEGREGATION, Y304-STRATEGY-PATTERN

**Pragmatic Exception:** Use ABC when you need shared implementation via inheritance (template method pattern), or when semantic inheritance is important for your domain.

---

## Y103-USE-GENERICS

**Description:** Use generic types (TypeVar, Generic) for reusable components that work with multiple types.

**Rationale:** Generics enable type-safe reuse without duplication. They preserve type information through transformations.

**Example:**
```python
from typing import TypeVar, Generic

T = TypeVar("T")

# Good - generic parser preserves type
class IOTool(Generic[T]):
    """Generic I/O tool for any item type."""
    def __init__(self, parser: Parser[T], producer: Producer[T]):
        self.parser = parser
        self.producer = producer

    def process(self, input_text: str) -> str:
        items: T = self.parser.parse(input_text)  # Type preserved
        return self.producer.produce(items)

# Usage - types are checked
visa_tool: IOTool[list[Transaction]] = IOTool(
    parser=VisaParser(),
    producer=TransactionProducer()
)

# Bad - loses type information
class IOTool:
    def __init__(self, parser, producer):
        self.parser = parser
        self.producer = producer
```

**Tool Support:** mypy checks generic type consistency. Use `Generic[T]` from `typing`.

**Related:** Y100-USE-TYPE-HINTS, Y101-PRECISE-TYPES

---

## Y104-TYPE-ALIASES

**Description:** Use type aliases for complex types. Use `TypeAlias` annotation for clarity.

**Rationale:** Type aliases improve readability, reduce duplication, and centralize type definitions.

**Example:**
```python
from typing import TypeAlias

# Good - clear and reusable
TransactionList: TypeAlias = list[Transaction]
ConfigDict: TypeAlias = dict[str, str | int | bool]
ParseResult: TypeAlias = tuple[bool, TransactionList | None, str | None]

def parse_file(path: str) -> ParseResult:
    """Returns (success, transactions, error_message)."""
    ...

# Bad - repeated complex type
def parse_file(path: str) -> tuple[bool, list[Transaction] | None, str | None]:
    ...

def validate_file(path: str) -> tuple[bool, list[Transaction] | None, str | None]:
    ...
```

**Tool Support:** Use `TypeAlias` from `typing` (Python 3.10+) or `typing_extensions`.

**Related:** Y105-NEWTYPE, Y101-PRECISE-TYPES

---

## Y105-NEWTYPE

**Description:** Use `NewType` to create distinct types from primitives when semantic distinction is important.

**Rationale:** NewType prevents mixing semantically different values of the same primitive type (e.g., user_id vs transaction_id).

**Example:**
```python
from typing import NewType

# Good - prevents mixing IDs
UserId = NewType("UserId", int)
TransactionId = NewType("TransactionId", int)

def get_user(user_id: UserId) -> User:
    ...

def get_transaction(txn_id: TransactionId) -> Transaction:
    ...

user_id = UserId(123)
txn_id = TransactionId(456)

get_user(user_id)  # OK
get_user(txn_id)   # mypy error: Expected UserId, got TransactionId

# Bad - no distinction
def get_user(user_id: int) -> User:
    ...

get_user(456)  # Accidentally passed transaction_id - no error!
```

**Tool Support:** mypy enforces NewType distinctions.

**Pragmatic Exception:** Don't overuse. Only create NewTypes when semantic confusion is a real risk.

**Related:** Y104-TYPE-ALIASES, Y100-USE-TYPE-HINTS

---

## Y106-COLLECTION-TYPES

**Description:** Use appropriate collection types from `collections.abc`: Sequence, Mapping, Iterable, Iterator, Collection.

**Rationale:** Abstract collection types are more flexible than concrete types, enabling broader compatibility.

**Example:**
```python
from collections.abc import Sequence, Mapping, Iterable

# Good - flexible input, specific output
def format_transactions(txns: Iterable[Transaction]) -> list[str]:
    """Accepts any iterable, returns specific list."""
    return [f"{t.date}: {t.amount}" for t in txns]

# Can pass list, tuple, generator, etc.
format_transactions([t1, t2, t3])  # list
format_transactions((t1, t2))       # tuple
format_transactions(t for t in txns if t.amount > 100)  # generator

# Good - read-only mapping
def apply_categories(txn: Transaction, categories: Mapping[str, str]) -> Transaction:
    """Applies categories, doesn't modify mapping."""
    category = categories.get(txn.merchant, "Other")
    return replace(txn, category=category)

# Bad - too restrictive
def format_transactions(txns: list[Transaction]) -> list[str]:
    return [f"{t.date}: {t.amount}" for t in txns]
```

**Collection Types:**
- `Iterable[T]`: Can be iterated (for loop), one pass
- `Sequence[T]`: Ordered, indexed, can iterate multiple times (list, tuple)
- `Mapping[K, V]`: Key-value pairs, read-only (dict, but immutable view)
- `MutableMapping[K, V]`: Mutable key-value pairs
- `Collection[T]`: Has length, contains checks, iterable

**Tool Support:** Import from `collections.abc` (not `typing`). mypy checks compatibility.

**Related:** Y101-PRECISE-TYPES, Y400-IMMUTABILITY

---

## Y107-LITERAL-TYPES

**Description:** Use `Literal` for values that must be specific constants.

**Rationale:** Literal types provide compile-time checking for magic strings/numbers, preventing typos.

**Example:**
```python
from typing import Literal

# Good - only specific values allowed
OutputFormat = Literal["csv", "json", "html"]

def export_data(data: list[Transaction], format: OutputFormat) -> str:
    if format == "csv":
        return to_csv(data)
    elif format == "json":
        return to_json(data)
    elif format == "html":
        return to_html(data)
    # mypy knows all cases are covered

# Usage
export_data(txns, "csv")    # OK
export_data(txns, "xml")    # mypy error: "xml" not in Literal["csv", "json", "html"]

# Bad - any string accepted
def export_data(data: list[Transaction], format: str) -> str:
    if format == "csv":
        return to_csv(data)
    elif format == "json":
        return to_json(data)
    elif format == "htlm":  # Typo not caught!
        return to_html(data)
```

**Tool Support:** `Literal` from `typing`. mypy checks exhaustiveness.

**Related:** Y108-FINAL, Y101-PRECISE-TYPES

---

## Y108-FINAL

**Description:** Use `Final` for constants that should never be reassigned.

**Rationale:** Final prevents accidental modification of constants, documents immutability intent.

**Example:**
```python
from typing import Final

# Good - constants are Final
DEFAULT_DATE_FORMAT: Final = "%Y-%m-%d"
MAX_RETRIES: Final = 3
API_BASE_URL: Final = "https://api.example.com"

# Attempt to reassign
DEFAULT_DATE_FORMAT = "%m/%d/%Y"  # mypy error: Cannot assign to final name

# Good - Final class attribute
class Config:
    DATABASE_URL: Final = "postgresql://localhost/db"
    TIMEOUT: Final = 30

# Bad - mutable constant (no Final)
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATE_FORMAT = "%m/%d/%Y"  # Accidentally modified, no error!
```

**Tool Support:** `Final` from `typing`. mypy enforces finality.

**Related:** Y400-IMMUTABILITY, Y107-LITERAL-TYPES

---

## Y109-AVOID-ANY

**Description:** Avoid `Any` type unless absolutely necessary. Use generics, unions, or protocols instead.

**Rationale:** Any disables type checking, defeating the purpose of type hints. It's a type system escape hatch.

**Example:**
```python
from typing import Any, TypeVar, Generic

T = TypeVar("T")

# Good - generic preserves type
def first(items: Sequence[T]) -> T | None:
    """Get first item, preserving type."""
    return items[0] if items else None

result: int | None = first([1, 2, 3])  # Type is int | None

# Bad - loses type information
def first(items: Sequence[Any]) -> Any:
    return items[0] if items else None

result: Any = first([1, 2, 3])  # Type is Any, no checking!

# Good - union for mixed types
def process_value(value: int | str | float) -> str:
    return str(value)

# Bad - Any for mixed types
def process_value(value: Any) -> str:
    return str(value)
```

**Tool Support:** mypy --strict warns on implicit Any.

**Pragmatic Exception:** Use Any when:
1. Interfacing with truly dynamic code (e.g., JSON parsing before validation)
2. Gradual typing migration (temporary, document plan to remove)
3. Type is genuinely unknowable (rare)

Always document why Any is needed.

**Related:** Y103-USE-GENERICS, Y101-PRECISE-TYPES, Z200-OVERUSE-ANY
