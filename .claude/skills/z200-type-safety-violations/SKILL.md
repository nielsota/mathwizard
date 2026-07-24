---
name: z200-type-safety-violations
description: Python type safety anti-patterns (Z200-Z215). Use when reviewing code for overuse of Any, missing type hints, type ignore comments, or other type safety violations.
---

# Type Safety Violations (Z200-Z215)

## 10. Type Safety Violations (Z200-Z215)

### **Z200-OVERUSE-ANY**
**Description:** Using `Any` everywhere instead of proper types.
**Why Bad:** Defeats type checking, loses safety.
**Better:** Y109-AVOID-ANY, Y103-USE-GENERICS

### **Z201-MISSING-RETURN-TYPE**
**Description:** Functions without return type annotations.
**Why Bad:** Unclear contract, no type checking.
**Better:** Y115-RETURN-TYPE-HINTS

### **Z202-IGNORING-TYPE-ERRORS**
**Description:** Using `# type: ignore` comments instead of fixing root causes.
**Why Bad:** Hides real problems, prevents type checking benefits, causes maintenance issues.
**Common Causes:**
- Documenting contracts in docstrings instead of defining them in code (use Y127-DEFINE-CONTRACTS-IN-CODE)
- Missing base class attributes (define them explicitly)
- Imprecise types (use Y101-PRECISE-TYPES)
**Better:** Fix the underlying type issue rather than suppressing the error. Define contracts in code, not documentation.

### **Z203-TYPE-CASTING-WITHOUT-VALIDATION**
**Description:** `cast(Type, value)` without runtime check.
**Why Bad:** Unsafe, can crash at runtime.
**Better:** Use Y111-TYPE-NARROWING with isinstance.

### **Z204-IMPLICIT-OPTIONAL**
**Description:** `def func(x: int = None)` without `| None`.
**Why Bad:** Type checker error, unclear intent.
**Better:** `def func(x: int | None = None)`

### **Z205-MIXED-TYPES-COLLECTIONS**
**Description:** `List[Union[int, str, dict]]` grab bag.
**Why Bad:** Hard to use safely, unclear purpose.
**Better:** Define proper types or use Y103-USE-GENERICS.

### **Z206-UNTYPED-DICTS**
**Description:** `Dict[str, Any]` for structured data.
**Why Bad:** No validation, no IDE support.
**Better:** Y112-DATACLASS-TYPES, TypedDict

### **Z207-MISSING-PARAMETER-TYPES**
**Description:** Function parameters without type hints.
**Why Bad:** Unclear expectations, no checking.
**Better:** Y100-USE-TYPE-HINTS

### **Z208-RETURN-MULTIPLE-TYPES**
**Description:** Returning different types without union.
**Example:** `return "error"` sometimes, `return 0` other times.
**Why Bad:** Unclear contract.
**Better:** Y110-UNION-TYPES or raise exception.

### **Z209-MUTABLE-DEFAULTS**
**Description:** `def func(items=[])`  or `def func(config={})`.
**Why Bad:** Shared mutable default across calls, classic Python gotcha.
**Better:** Y413-AVOID-MUTABLE-DEFAULTS

### **Z210-MISSING-PROTOCOL-METHODS**
**Description:** Class claims to implement protocol but missing methods.
**Why Bad:** Runtime AttributeError.
**Better:** Use Y102-USE-PROTOCOLS correctly, test compliance.

### **Z211-WRONG-VARIANCE**
**Description:** Covariant/contravariant used incorrectly.
**Why Bad:** Type safety violated.
**Better:** Study variance rules, use TypeVar correctly.

### **Z212-ISINSTANCE-ON-TYPING**
**Description:** `isinstance(x, List[int])` doesn't work.
**Why Bad:** Runtime type info lost for generics.
**Better:** `isinstance(x, list)` and validate elements manually.

### **Z213-MIXED-SYNC-ASYNC**
**Description:** Confusing sync/async in type hints.
**Why Bad:** Runtime errors, unclear behavior.
**Better:** Consistent async types, use `Awaitable`.

### **Z214-UNION-NONE-LAST**
**Description:** `None | int` instead of `int | None`.
**Why Bad:** Convention is None last.
**Better:** `int | None` for consistency.

### **Z215-DATACLASS-WITH-BEHAVIOR**
**Description:** Using `@dataclass` decorator for classes with complex behavior, business logic, or methods beyond simple accessors.
**Why Bad:** Dataclasses are designed for "dumb" data containers (DTOs, value objects) that primarily hold data. Using them for classes with behavior:
- Confuses the purpose of the class (is it data or behavior?)
- Encourages mixing data representation with business logic
- Makes it harder to test (behavior mixed with data initialization)
- Violates Y200-SINGLE-RESPONSIBILITY (data structure + behavior = two responsibilities)
**Examples:**
```python
# Bad - Strategy with behavior as dataclass
@dataclass(frozen=True)
class RebalanceStrategy(Strategy):
    target_allocations: dict[str, float]

    def generate_actions(self, date: date, portfolio: Portfolio) -> Iterator[Action]:
        # Complex rebalancing logic here...
        pass  # This is behavior, not data!

# Bad - Service with methods as dataclass
@dataclass
class TransactionProcessor:
    config: Config

    def process(self, txn: Transaction) -> Result:
        # Complex processing logic...
        pass

# Good - Strategy with behavior as regular class
class RebalanceStrategy(Strategy):
    def __init__(self, target_allocations: dict[str, float]) -> None:
        """Initialize rebalancing strategy."""
        if not (0.999 <= sum(target_allocations.values()) <= 1.001):
            raise ValueError("Allocations must sum to 1.0")
        self._target_allocations = target_allocations

    def generate_actions(self, date: date, portfolio: Portfolio) -> Iterator[Action]:
        # Complex rebalancing logic here...
        pass

# Good - Data container as dataclass
@dataclass(frozen=True)
class Transaction:
    """Dumb data container for transaction record."""
    id: int
    date: date
    amount: Decimal
    merchant: str
    category: str | None = None
    # No methods with business logic - just data!

# Good - Action parameter container as dataclass
@dataclass(frozen=True)
class BuyAction(Action):
    """Encapsulates buy parameters - minimal behavior."""
    asset_id: str
    date: date
    units: float | None
    value: float | None

    def execute(self, portfolio: Portfolio) -> ActionResult:
        # Minimal behavior: just delegates to portfolio
        return portfolio.buy(...)
```
**When to use dataclasses:**
- DTOs (Data Transfer Objects) between layers
- Value objects (immutable data with no behavior)
- Configuration containers (just data fields)
- Action parameters (Command pattern parameters)
- Test fixtures (simple data for tests)

**When NOT to use dataclasses:**
- Strategy implementations (Y304-STRATEGY-PATTERN)
- Service classes with business logic
- Controllers/Managers with orchestration logic
- Parsers/Processors with complex algorithms
- Any class where behavior > data

**Better:** Use regular classes with explicit `__init__` for classes with behavior. Reserve dataclasses for Y112-DATACLASS-TYPES (data containers).
