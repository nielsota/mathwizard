---
name: y400-functional-programming
description: Python functional programming guidelines (Y400-Y424). Use when writing immutable data structures, pure functions, generators, comprehensions, or applying functools/itertools patterns.
---

# Functional Programming (Y400-Y424)

## 4. Functional Programming (Y400-Y424)

### **Y400-IMMUTABILITY**
**Description:** Prefer immutable data structures. Use `frozen=True` for dataclasses.
**Example:** `@dataclass(frozen=True)` prevents modification after creation.
**Related:** Y401-FROZEN-DATACLASSES, Y114-NAMEDTUPLE-TYPES

### **Y401-FROZEN-DATACLASSES**
**Description:** Use `frozen=True` for dataclasses that shouldn't change.
**Example:** `@dataclass(frozen=True) class Transaction: ...`
**Related:** Y112-DATACLASS-TYPES, Y400-IMMUTABILITY

### **Y402-PURE-FUNCTIONS**
**Description:** Functions without side effects, same input → same output.
**Example:** `def calculate_tax(amount: Decimal) -> Decimal: return amount * TAX_RATE`
**Related:** Y403-AVOID-SIDE-EFFECTS

### **Y403-AVOID-SIDE-EFFECTS**
**Description:** Don't modify arguments or global state. Return new values.
**Example:** `def uppercase_merchant(txn: Transaction) -> Transaction: return replace(txn, merchant=txn.merchant.upper())`
**Related:** Y402-PURE-FUNCTIONS, Z300-MUTATING-ARGUMENTS

### **Y404-RETURN-NEW-VALUES**
**Description:** Return new objects instead of modifying existing ones.
**Example:** Use `dataclasses.replace()` to create modified copy.
**Related:** Y400-IMMUTABILITY

### **Y405-GENERATORS**
**Description:** Use generators with `yield` for lazy evaluation and memory efficiency. Generators compute values on-demand rather than creating entire sequences in memory.

**Return Type:** Annotate with `Iterator[T]` from `collections.abc`, not `tuple` or `list`.

**When to Use:**
- Processing large datasets or files line-by-line
- Transforming sequences where not all values may be consumed
- Creating infinite sequences
- Chaining operations that don't need materialization

**Example:**
```python
from collections.abc import Iterator
from datetime import date

def enumerate_months(start: date, end: date) -> Iterator[date]:
    """Generate month boundaries lazily."""
    current = start.replace(day=1)
    end_month = end.replace(day=1)
    while current <= end_month:
        yield current
        current = current + relativedelta(months=1)

# Caller decides when to materialize
months_list = list(enumerate_months(start, end))  # Only if needed
```

**Anti-Pattern:** Building lists unnecessarily:
```python
# DON'T: Eager evaluation uses more memory
def enumerate_months(...) -> tuple[date, ...]:
    months = []
    while ...:
        months.append(current)
    return tuple(months)
```

**Related:** Y406-LAZY-EVALUATION, Y802-GENERATOR-VS-LIST, Y314-ITERATOR-PATTERN

### **Y406-LAZY-EVALUATION**
**Description:** Prefer lazy evaluation over eager computation. Compute values only when actually needed. This reduces memory usage, enables working with infinite sequences, and can improve performance by avoiding unnecessary computation.

**Key Techniques:**
- Generators and generator expressions (not list comprehensions)
- `itertools` for lazy transformations (chain, islice, takewhile, etc.)
- Return `Iterator[T]` instead of `list[T]` or `tuple[T]` when possible
- Let callers materialize with `list()` only if they need the full sequence

**Example:**
```python
from collections.abc import Iterator
from itertools import chain, islice

# GOOD: Lazy - only computes what's consumed
def process_transactions(file) -> Iterator[Transaction]:
    for line in file:
        yield parse_transaction(line)

# Caller controls materialization
txns = process_transactions(file)
first_ten = list(islice(txns, 10))  # Only parses 10 lines

# GOOD: Chain multiple generators
def all_files(dirs: list[Path]) -> Iterator[Path]:
    return chain.from_iterable(d.iterdir() for d in dirs)

# BAD: Eager - loads everything into memory
def process_transactions(file) -> list[Transaction]:
    return [parse_transaction(line) for line in file]  # All at once!
```

**Performance Benefits:**
- Memory: O(1) vs O(n) for large sequences
- Speed: Can start consuming immediately (no upfront delay)
- Composability: Chain operations without intermediate lists

**Trade-offs:**
- Can only iterate once (unless using `itertools.tee()`)
- Can't index or get length without consuming
- Debugging harder (can't inspect full sequence)

**When to Materialize:**
- Need random access or indexing
- Need length without consuming
- Need to iterate multiple times
- Returning from API where caller doesn't control iteration

**Related:** Y405-GENERATORS, Y410-ITERTOOLS, Y802-GENERATOR-VS-LIST

### **Y407-COMPREHENSIONS**
**Description:** Use list/dict/set comprehensions for transformations.
**Example:** `[txn.amount for txn in txns if txn.amount > 100]`
**Related:** Y408-MAP-FILTER

### **Y408-MAP-FILTER**
**Description:** Prefer comprehensions over `map()`/`filter()` for clarity.
**Example:** `[x*2 for x in nums]` clearer than `list(map(lambda x: x*2, nums))`.
**Pragmatic:** Use `map`/`filter` when you already have a named function.

### **Y409-FUNCTOOLS**
**Description:** Use functools for functional patterns: `reduce`, `partial`, `lru_cache`.
**Example:** `from functools import lru_cache; @lru_cache; def expensive(...): ...`
**Related:** Y804-CACHING

### **Y410-ITERTOOLS**
**Description:** Use itertools for efficient iteration patterns.
**Example:** `itertools.chain()`, `groupby()`, `accumulate()`.
**Related:** Y405-GENERATORS

### **Y411-OPERATOR-MODULE**
**Description:** Use `operator` module instead of lambdas for common operations.
**Example:** `sorted(txns, key=operator.attrgetter('date'))` not `sorted(txns, key=lambda t: t.date)`.

### **Y412-DATACLASS-REPLACE**
**Description:** Use `dataclasses.replace()` for immutable updates.
**Example:** `updated = replace(txn, amount=Decimal("100"))`.
**Related:** Y400-IMMUTABILITY

### **Y413-AVOID-MUTABLE-DEFAULTS**
**Description:** Never use mutable default arguments.
**Example:** `def func(items: list[int] | None = None)` not `def func(items: list[int] = [])`.
**Related:** Z209-MUTABLE-DEFAULTS

### **Y414-CLOSURES**
**Description:** Use closures for encapsulation and factory functions.
**Example:** `def make_adder(n): return lambda x: x + n`.

### **Y415-FIRST-CLASS-FUNCTIONS**
**Description:** Pass functions as arguments, return from functions.
**Example:** `def apply(f: Callable, x): return f(x)`.
**Related:** Y113-CALLABLE-TYPES

### **Y416-HIGHER-ORDER-FUNCTIONS**
**Description:** Functions that take or return functions.
**Example:** Decorators, `sorted(key=...)`, `map()`, `filter()`.
**Related:** Y311-DECORATOR-PATTERN

### **Y417-RECURSION**
**Description:** Use recursion for naturally recursive problems (trees, etc.).
**Pragmatic:** Python has recursion limit (~1000). Use iteration for deep structures.

### **Y418-TAIL-RECURSION**
**Description:** Python doesn't optimize tail recursion. Use iteration instead.
**Example:** Use `while` loop, not tail-recursive function.

### **Y419-IMMUTABLE-COLLECTIONS**
**Description:** Use `tuple`, `frozenset` for immutable collections.
**Example:** `ALLOWED_CATEGORIES: Final = frozenset(["Food", "Transport"])`.
**Related:** Y108-FINAL

### **Y420-AVOID-GLOBALS**
**Description:** Minimize global mutable state. Use parameters/returns.
**Example:** Pass configuration as parameter, don't use global config dict.
**Related:** Z301-GLOBAL-STATE

### **Y421-REFERENTIAL-TRANSPARENCY**
**Description:** Function calls can be replaced with their return values.
**Example:** Pure functions are referentially transparent.
**Related:** Y402-PURE-FUNCTIONS

### **Y422-PIPELINE-PATTERN**
**Description:** Chain transformations using function composition.
**Example:** `data |> parse |> validate |> transform` (via libraries or custom operator).
**Related:** Y405-GENERATORS

### **Y423-MONADS**
**Description:** Consider Result/Option types for error handling (via libraries).
**Example:** `Result[T, Error]` instead of exceptions for expected failures.
**Pragmatic:** Python idiom uses exceptions; monads less common.

### **Y424-PARTIAL-APPLICATION**
**Description:** Use `functools.partial` to pre-fill function arguments.
**Example:** `from functools import partial; process_all = partial(map, process_one)`.
**Related:** Y409-FUNCTOOLS
