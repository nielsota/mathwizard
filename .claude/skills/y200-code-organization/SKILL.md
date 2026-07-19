---
name: y200-code-organization
description: Python code organization and modularity guidelines (Y200-Y224). Use when structuring modules, organizing imports, applying dependency injection, or designing package architecture.
---

# Code Organization & Modularity (Y200-Y224)

## 2. Code Organization & Modularity (Y200-Y224)

### **Y200-SINGLE-RESPONSIBILITY**
**Description:** Each class/module should have one reason to change (SRP).
**Example:** Separate `Parser` (reads data) from `Validator` (checks data) from `Transformer` (converts data).
**Related:** Y202-SEPARATION-OF-CONCERNS, Z102-GOD-OBJECTS

### **Y201-INTERFACE-SEGREGATION**
**Description:** Many small, specific interfaces better than one large interface.
**Example:** `Readable`, `Writable`, `Seekable` protocols instead of one `File` interface.
**Related:** Y102-USE-PROTOCOLS, Y203-DEPENDENCY-INJECTION

### **Y202-SEPARATION-OF-CONCERNS**
**Description:** Separate business logic, data access, presentation, and infrastructure.
**Example:** `TransactionRepository` (data), `TransactionService` (logic), `TransactionAPI` (presentation).
**Related:** Y200-SINGLE-RESPONSIBILITY

### **Y203-DEPENDENCY-INJECTION**
**Description:** Pass dependencies as parameters, don't create them internally.
**Example:** `IOTool(parser=VisaParser(), producer=CSVProducer())` not `IOTool()` that creates them internally.
**Related:** Y201-INTERFACE-SEGREGATION, Y304-STRATEGY-PATTERN

### **Y204-DEPENDENCY-INVERSION**
**Description:** Depend on abstractions (protocols), not concretions.
**Example:** `def process(parser: Parser[T])` not `def process(parser: VisaParser)`.
**Related:** Y102-USE-PROTOCOLS

### **Y205-OPEN-CLOSED**
**Description:** Open for extension, closed for modification. Extend behavior without changing existing code.
**Example:** `EventProducer` extends `Producer` with date filtering without modifying `Producer`.
**Related:** Y304-STRATEGY-PATTERN, Y308-TEMPLATE-METHOD

### **Y206-MODULE-STRUCTURE**
**Description:** Organize modules by feature/domain, not by type.
**Example:** `banking/visa/`, `banking/sepa/` not `models/`, `parsers/`, `validators/`.
**Related:** Y200-SINGLE-RESPONSIBILITY

### **Y207-PACKAGE-INIT**
**Description:** Use `__init__.py` to expose public API using `from ... import *` pattern.
**Example:**
```python
# In __init__.py
from ._parser import *
from ._producer import *
```
Each private module defines its own `__all__` to control what gets exported.
**Anti-pattern:** Don't explicitly import and list names in `__init__.py` - use wildcard imports instead.
**Related:** Y208-PUBLIC-API

### **Y208-PUBLIC-API**
**Description:** Define `__all__` in each module (not in `__init__.py`) to control public API.
**Example:**
```python
# In _parser.py
__all__ = ["VisaParser", "SepaParser"]

class VisaParser:
    ...

class SepaParser:
    ...

class _InternalHelper:  # Not in __all__, remains private
    ...
```
The package `__init__.py` uses `from ._parser import *` to re-export these names.
**Tool Support:** ruff checks `__all__` consistency.
**Related:** Y207-PACKAGE-INIT

### **Y209-IMPORT-STYLE**
**Description:** Prefer absolute imports. Use relative imports only within packages.
**Example:** `from src.util.parser import Parser` not `from ..util.parser import Parser` in scripts.
**Tool Support:** ruff rule I001-I005 enforce import style.

### **Y210-IMPORT-ORDER**
**Description:** Standard library, third-party, local. Alphabetical within groups.
**Tool Support:** ruff I001 enforces isort-compatible ordering.
**Pragmatic:** Pre-commit hooks auto-format this.

### **Y211-CIRCULAR-IMPORTS**
**Description:** Avoid circular dependencies. Use protocols or TYPE_CHECKING.
**Example:** See Y120-TYPE-CHECKING for avoiding circular imports.
**Related:** Y120-TYPE-CHECKING, Z101-CIRCULAR-DEPS

### **Y212-LAZY-IMPORTS**
**Description:** Import at module level by default. Use local imports only for optional dependencies or circular imports.
**Example:** `if TYPE_CHECKING: from expensive_module import Heavy` to avoid runtime cost.
**Related:** Y120-TYPE-CHECKING

### **Y213-COHESION**
**Description:** Related functionality should be together. High cohesion within modules.
**Example:** All VISA parsing logic in `visa.py`, not scattered across multiple files.
**Related:** Y200-SINGLE-RESPONSIBILITY

### **Y214-COUPLING**
**Description:** Minimize dependencies between modules. Loose coupling preferred.
**Example:** Use events/callbacks instead of direct method calls between unrelated modules.
**Related:** Z100-TIGHT-COUPLING, Y203-DEPENDENCY-INJECTION

### **Y215-FLAT-OVER-NESTED**
**Description:** Prefer flat module structure over deep nesting.
**Example:** `banking_visa.py`, `banking_sepa.py` not `banking/transactions/visa/parser.py` with 5 levels.
**Pragmatic:** 2-3 levels maximum unless truly necessary.

### **Y216-EXPLICIT-EXPORTS**
**Description:** Be explicit when importing from other modules. Avoid `import *` in application code.
**Example:** Import specific names: `from cashflow.market import ETFAsset, MarketContext` not `from cashflow.market import *`.
**Exception:** Wildcard imports (`from ._module import *`) are appropriate in `__init__.py` files for re-exporting public APIs (see Y207-PACKAGE-INIT).
**Tool Support:** ruff F403 warns on wildcard imports (except in `__init__.py`).
**Related:** Y207-PACKAGE-INIT, Y208-PUBLIC-API

### **Y217-TYPE-STUBS**
**Description:** For untyped third-party libs, use stub files or `py.typed`.
**Example:** `pandas-stubs` for pandas type hints.
**Related:** Y100-USE-TYPE-HINTS

### **Y218-NAMESPACE-PACKAGES**
**Description:** Avoid namespace packages unless distributing plugins.
**Example:** Use regular packages with `__init__.py` for standard projects.

### **Y219-PRIVATE-MODULES**
**Description:** Use `_module.py` prefix for internal/private modules.
**Example:** `_internal.py`, `_helpers.py` signal "don't import from external code".

### **Y220-CONSTANTS-MODULE**
**Description:** Group constants in dedicated module when many exist.
**Example:** `config.py` with `DATE_FORMAT`, `MAX_RETRIES`, etc.
**Related:** Y108-FINAL

### **Y221-UTILS-ANTIPATTERN**
**Description:** Avoid catch-all `utils` modules. Use specific names.
**Example:** `date_helpers.py`, `string_formatters.py` not `utils.py` with everything.
**Related:** Y200-SINGLE-RESPONSIBILITY, Z401-WRONG-ABSTRACTION-LEVEL

### **Y222-FACADE-PATTERN**
**Description:** Provide simple interface to complex subsystem.
**Example:** `BankingAPI` class that hides complexity of parsers, validators, converters.
**Related:** Y310-FACADE-PATTERN

### **Y223-COMPOSITION-OVER-INHERITANCE**
**Description:** Prefer composition (has-a) over inheritance (is-a).
**Example:** `IOTool` has `Parser` and `Producer` (composition) rather than inheriting from both.
**Related:** Y203-DEPENDENCY-INJECTION

### **Y224-ADAPTER-PATTERN**
**Description:** Convert interface of one class to another.
**Example:** `PandasDataFrameAdapter` implements `Iterable[Transaction]` protocol for DataFrame.
**Related:** Y309-ADAPTER-PATTERN
