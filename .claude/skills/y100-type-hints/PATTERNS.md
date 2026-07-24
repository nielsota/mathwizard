# Type Hints Patterns (Y110-Y117)

Guidelines for common type hint patterns including unions, type narrowing, dataclasses, and method typing.

---

## Y110-UNION-TYPES

**Description:** Use modern union syntax `X | Y` (Python 3.10+) instead of `Union[X, Y]` or `Optional[X]`.

**Rationale:** Cleaner syntax, more readable, aligns with PEP 604.

**Example:**
```python
# Good - modern syntax (Python 3.10+)
def parse_amount(value: str | int | float) -> float:
    """Parse amount from multiple types."""
    if isinstance(value, str):
        return float(value.replace(",", ""))
    return float(value)

def find_transaction(txn_id: int) -> Transaction | None:
    """Returns transaction or None if not found."""
    ...

# Bad - old syntax (pre-3.10)
from typing import Union, Optional

def parse_amount(value: Union[str, int, float]) -> float:
    ...

def find_transaction(txn_id: int) -> Optional[Transaction]:
    ...
```

**Tool Support:** Python 3.10+ required. mypy supports both syntaxes.

**Related:** Y100-USE-TYPE-HINTS, Y101-PRECISE-TYPES

---

## Y111-TYPE-NARROWING

**Description:** Use type narrowing with isinstance(), is None checks, and TypeGuard for complex narrowing.

**Rationale:** Type narrowing helps mypy understand conditional type refinement, reducing false positives.

**Example:**
```python
from typing import TypeGuard

# Good - isinstance narrows type
def process_value(value: int | str) -> str:
    if isinstance(value, int):
        # mypy knows value is int here
        return str(value * 2)
    else:
        # mypy knows value is str here
        return value.upper()

# Good - is None narrows Optional
def get_name(user: User | None) -> str:
    if user is None:
        return "Unknown"
    # mypy knows user is not None here
    return user.name

# Good - TypeGuard for custom narrowing
def is_non_empty_list(val: Sequence[T] | None) -> TypeGuard[Sequence[T]]:
    """Type guard that ensures non-empty sequence."""
    return val is not None and len(val) > 0

def process_items(items: Sequence[Transaction] | None) -> None:
    if is_non_empty_list(items):
        # mypy knows items is Sequence[Transaction] (not None)
        first_item = items[0]  # No error
        ...
```

**Tool Support:** mypy performs automatic narrowing for isinstance, is None. TypeGuard from `typing` for custom guards.

**Related:** Y100-USE-TYPE-HINTS, Y110-UNION-TYPES

---

## Y112-DATACLASS-TYPES

**Description:** Use dataclasses with full type hints for data containers.

**Rationale:** Dataclasses reduce boilerplate, integrate with type checking, and provide immutability options.

**Example:**
```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# Good - typed dataclass
@dataclass(frozen=True)  # Immutable
class Transaction:
    """Represents a financial transaction."""
    id: int
    date: date
    amount: Decimal
    merchant: str
    category: str | None = None

# All attributes are typed, immutable, have __repr__, __eq__, etc.
txn = Transaction(
    id=1,
    date=date(2025, 1, 15),
    amount=Decimal("99.99"),
    merchant="Amazon"
)

# Bad - manual class with no types
class Transaction:
    def __init__(self, id, date, amount, merchant, category=None):
        self.id = id
        self.date = date
        self.amount = amount
        self.merchant = merchant
        self.category = category
    # Missing: __repr__, __eq__, type hints, immutability
```

**Tool Support:** Dataclasses from `dataclasses` module (Python 3.7+). mypy checks field types.

**Related:** Y400-IMMUTABILITY, Y401-FROZEN-DATACLASSES, Y100-USE-TYPE-HINTS

---

## Y113-CALLABLE-TYPES

**Description:** Use Callable type hint for functions passed as parameters.

**Rationale:** Documents expected function signature, enables type checking of callbacks.

**Example:**
```python
from collections.abc import Callable

# Good - precise Callable type
def apply_to_transactions(
    transactions: list[Transaction],
    transform: Callable[[Transaction], Transaction]
) -> list[Transaction]:
    """Apply transform to each transaction."""
    return [transform(txn) for txn in transactions]

def uppercase_merchant(txn: Transaction) -> Transaction:
    return replace(txn, merchant=txn.merchant.upper())

# Usage - type checked
result = apply_to_transactions(txns, uppercase_merchant)  # OK

# Error caught
def bad_transform(txn: Transaction) -> str:  # Wrong return type!
    return txn.merchant

apply_to_transactions(txns, bad_transform)  # mypy error

# Bad - no Callable type
def apply_to_transactions(transactions, transform):
    return [transform(txn) for txn in transactions]
```

**Tool Support:** Callable from `collections.abc`. Syntax: `Callable[[ArgTypes...], ReturnType]`.

**Related:** Y100-USE-TYPE-HINTS, Y304-STRATEGY-PATTERN

---

## Y114-NAMEDTUPLE-TYPES

**Description:** Use NamedTuple with type hints for simple immutable data structures.

**Rationale:** NamedTuples are immutable, lightweight, and have good performance. Better than plain tuples.

**Example:**
```python
from typing import NamedTuple
from datetime import date
from decimal import Decimal

# Good - typed NamedTuple
class VisaBookingData(NamedTuple):
    """Raw VISA booking data from statement."""
    booking_date: date
    receipt_date: date
    amount: Decimal
    merchant: str
    location: str

# Usage
booking = VisaBookingData(
    booking_date=date(2025, 1, 15),
    receipt_date=date(2025, 1, 14),
    amount=Decimal("99.99"),
    merchant="Amazon",
    location="Online"
)

# Immutable - booking.amount = Decimal("100.00") raises AttributeError

# Good indexing and attributes
print(booking[0])     # date(2025, 1, 15)
print(booking.amount) # Decimal('99.99')

# Bad - plain tuple (no attribute access, no type hints, unclear meaning)
booking = (date(2025, 1, 15), date(2025, 1, 14), Decimal("99.99"), "Amazon", "Online")
```

**When to use:**
- NamedTuple: Simple, immutable data with few fields
- dataclass: More complex data, needs methods, optional mutability
- Plain tuple: Only for very short-lived, obvious positional data

**Tool Support:** NamedTuple from `typing`. mypy checks field types.

**Related:** Y112-DATACLASS-TYPES, Y400-IMMUTABILITY

---

## Y115-RETURN-TYPE-HINTS

**Description:** Always specify return types, even for functions returning None.

**Rationale:** Explicit return types document intent, catch missing returns, and enable better type inference.

**Example:**
```python
# Good - explicit return types
def parse_line(line: str) -> Transaction | None:
    """Parse line, returns None if invalid."""
    if not line.strip():
        return None
    return Transaction(...)

def log_transaction(txn: Transaction) -> None:
    """Log transaction, returns nothing."""
    print(f"Transaction: {txn.id}")
    # Explicit None documents side-effect-only function

def process_batch(txns: list[Transaction]) -> tuple[int, int]:
    """Process transactions, returns (success_count, error_count)."""
    success, errors = 0, 0
    for txn in txns:
        if process_one(txn):
            success += 1
        else:
            errors += 1
    return success, errors

# Bad - no return types
def parse_line(line: str):  # Return type unclear
    if not line.strip():
        return None
    return Transaction(...)

def log_transaction(txn: Transaction):  # Looks like missing return?
    print(f"Transaction: {txn.id}")
```

**Tool Support:** mypy --strict requires return type annotations. ruff ANN201/ANN202 enforce.

**Related:** Y100-USE-TYPE-HINTS, Z201-MISSING-RETURN-TYPE

---

## Y116-CLASS-VAR

**Description:** Use ClassVar to annotate class variables (not instance variables).

**Rationale:** Distinguishes class-level from instance-level attributes, prevents mypy confusion.

**Example:**
```python
from typing import ClassVar

# Good - clear distinction
class Transaction:
    """Transaction with class-level config."""

    # Class variable - shared across all instances
    date_format: ClassVar[str] = "%Y-%m-%d"
    max_amount: ClassVar[Decimal] = Decimal("10000")

    # Instance variables
    id: int
    amount: Decimal

    def __init__(self, id: int, amount: Decimal):
        self.id = id
        self.amount = amount

    def format_date(self, date: date) -> str:
        return date.strftime(self.date_format)

# Usage
Transaction.date_format = "%m/%d/%Y"  # Changes for all instances

# Bad - ambiguous
class Transaction:
    date_format: str = "%Y-%m-%d"  # Is this class or instance var?
```

**Tool Support:** ClassVar from `typing`. mypy enforces correct usage.

**Related:** Y100-USE-TYPE-HINTS, Y112-DATACLASS-TYPES

---

## Y117-SELF-TYPE

**Description:** Use `Self` type for methods returning the instance (method chaining, factory methods).

**Rationale:** Self correctly handles inheritance, unlike hardcoded class names.

**Example:**
```python
from typing import Self

# Good - Self type
class Transaction:
    """Transaction with fluent interface."""

    def __init__(self, amount: Decimal):
        self.amount = amount
        self.category: str | None = None

    def with_category(self, category: str) -> Self:
        """Set category (fluent)."""
        self.category = category
        return self

    @classmethod
    def from_string(cls, text: str) -> Self:
        """Factory method returning Self."""
        amount = Decimal(text)
        return cls(amount)

# Works with inheritance
class DetailedTransaction(Transaction):
    def __init__(self, amount: Decimal, details: str):
        super().__init__(amount)
        self.details = details

# Correct return type preserved
dtxn: DetailedTransaction = (
    DetailedTransaction
    .from_string("100.50")  # Returns DetailedTransaction, not Transaction
    .with_category("Food")   # Still DetailedTransaction
)

# Bad - hardcoded class name
class Transaction:
    def with_category(self, category: str) -> Transaction:
        self.category = category
        return self

    @classmethod
    def from_string(cls, text: str) -> Transaction:  # Wrong for subclasses!
        return cls(Decimal(text))
```

**Tool Support:** Self from `typing` (Python 3.11+) or `typing_extensions`.

**Related:** Y103-USE-GENERICS, Y306-BUILDER-PATTERN
