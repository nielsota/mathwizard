---
name: y300-design-patterns
description: Python design patterns guidelines (Y300-Y334). Use when implementing factory, strategy, observer, decorator, or other design patterns in Python code.
---

# Design Patterns (Y300-Y334)

## 3. Design Patterns (Y300-Y334)

### **Y300-FACTORY-METHOD**
**Description:** Define interface for creating objects, let subclasses decide which class to instantiate.
**Example:** `Parser.create(format="visa")` returns `VisaParser` or `SepaParser`.
**Related:** Y117-SELF-TYPE

### **Y301-ABSTRACT-FACTORY**
**Description:** Create families of related objects without specifying concrete classes.
**Example:** `BankingFactory` creates matching parser, validator, and producer for a bank type.

### **Y302-BUILDER-PATTERN**
**Description:** Construct complex objects step by step.
**Example:** `TransactionBuilder().with_date(...).with_amount(...).build()`.
**Related:** Y117-SELF-TYPE, Y306-BUILDER-PATTERN

### **Y303-SINGLETON-PATTERN**
**Description:** Ensure class has only one instance. Use sparingly.
**Example:** Database connection pool, configuration manager.
**Pragmatic:** Often better as module-level instance or dependency injection.

### **Y304-STRATEGY-PATTERN**
**Description:** Define family of algorithms, make them interchangeable.
**Example:** Different `Parser` implementations, selected at runtime via `IOTool(parser=...)`.
**Related:** Y203-DEPENDENCY-INJECTION, Y113-CALLABLE-TYPES

### **Y305-OBSERVER-PATTERN**
**Description:** Define subscription mechanism to notify multiple objects of events.
**Example:** Event system where `TransactionProcessor` notifies listeners of completed transactions.

### **Y306-BUILDER-PATTERN**
**Description:** Separate construction from representation using fluent interface.
**Example:** `Query().filter(amount__gt=100).order_by("date").limit(10)`.
**Related:** Y117-SELF-TYPE

### **Y307-COMMAND-PATTERN**
**Description:** Encapsulate request as object, enabling queuing, logging, undo.
**Example:** `ParseCommand`, `ValidateCommand`, `TransformCommand` with `.execute()` method.

### **Y308-TEMPLATE-METHOD**
**Description:** Define algorithm skeleton, let subclasses override steps.
**Example:** ABC `Parser` with `parse()` that calls abstract `parse_line()`, `validate_line()`.
**Related:** Y102-USE-PROTOCOLS, Y205-OPEN-CLOSED

### **Y309-ADAPTER-PATTERN**
**Description:** Convert one interface to another clients expect.
**Example:** Adapt pandas DataFrame to `Sequence[Transaction]` protocol.
**Related:** Y224-ADAPTER-PATTERN

### **Y310-FACADE-PATTERN**
**Description:** Unified interface to set of interfaces in subsystem.
**Example:** `BankingAPI` hides complexity of parsing, validation, conversion.
**Related:** Y222-FACADE-PATTERN

### **Y311-DECORATOR-PATTERN**
**Description:** Add behavior to objects dynamically.
**Example:** `@log_calls`, `@retry`, `@cache` decorators that wrap functions.
**Related:** Y123-PARAMSPEC, Y124-CONCATENATE

### **Y312-PROXY-PATTERN**
**Description:** Provide placeholder/surrogate for another object.
**Example:** Lazy-loading proxy that loads data only when first accessed.

### **Y313-COMPOSITE-PATTERN**
**Description:** Compose objects into tree structures.
**Example:** `CompositeValidator` contains multiple validators, validates all.

### **Y314-ITERATOR-PATTERN**
**Description:** Access elements sequentially without exposing representation.
**Example:** `Parser` yields transactions one at a time with `yield`.
**Related:** Y405-GENERATORS, Y106-COLLECTION-TYPES

### **Y315-STATE-PATTERN**
**Description:** Change behavior when internal state changes.
**Example:** `Connection` with states: `Connected`, `Disconnected`, `Connecting`.

### **Y316-CHAIN-OF-RESPONSIBILITY**
**Description:** Pass request along chain until handled.
**Example:** Validation pipeline where each validator checks and passes to next.

### **Y317-MEDIATOR-PATTERN**
**Description:** Encapsulate how objects interact.
**Example:** `EventBus` mediates communication between publishers and subscribers.

### **Y318-MEMENTO-PATTERN**
**Description:** Capture and restore object state.
**Example:** Transaction history with undo/redo using snapshots.

### **Y319-VISITOR-PATTERN**
**Description:** Separate algorithm from object structure.
**Example:** `TransactionVisitor` with `visit_debit()`, `visit_credit()` methods.

### **Y320-NULL-OBJECT-PATTERN**
**Description:** Use object with do-nothing behavior instead of None checks.
**Example:** `NullLogger` that implements `Logger` but does nothing.
**Pragmatic:** Modern Python uses `Optional[T]` and explicit None checks instead.

### **Y321-REGISTRY-PATTERN**
**Description:** Global registry of objects by key.
**Example:** Parser registry: `register_parser("visa", VisaParser)`.

### **Y322-DEPENDENCY-CONTAINER**
**Description:** IoC container managing object creation and dependencies.
**Example:** Simple dict-based container for dependency injection.
**Related:** Y203-DEPENDENCY-INJECTION

### **Y323-REPOSITORY-PATTERN**
**Description:** Mediates between domain and data mapping layers.
**Example:** `TransactionRepository` with `.find_by_id()`, `.save()` methods.

### **Y324-SPECIFICATION-PATTERN**
**Description:** Business rules as composable objects.
**Example:** `AmountGreaterThan(100) & CategoryEquals("Food")` specifications.

### **Y325-EVENT-SOURCING**
**Description:** Store state changes as sequence of events.
**Example:** Transaction audit log with all state transitions.

### **Y326-FLYWEIGHT-PATTERN**
**Description:** Share common state to support large numbers of objects.
**Example:** String interning, cached immutable objects.
**Pragmatic:** Python does this automatically for small ints/strings.

### **Y327-PROTOTYPE-PATTERN**
**Description:** Clone objects instead of creating new ones.
**Example:** `copy.copy()` or `copy.deepcopy()` for cloning.
**Related:** Y400-IMMUTABILITY

### **Y328-BRIDGE-PATTERN**
**Description:** Decouple abstraction from implementation.
**Example:** Separate `Parser` (abstraction) from `LineReader` (implementation).

### **Y329-MONOSTATE-PATTERN**
**Description:** All instances share state (alternative to Singleton).
**Example:** Class where all instances access shared class variables.

### **Y330-OBJECT-POOL**
**Description:** Reuse expensive objects from pool.
**Example:** Database connection pool.

### **Y331-LAZY-INITIALIZATION**
**Description:** Defer expensive object creation until needed.
**Example:** `@cached_property` for expensive computed attributes.
**Tool Support:** `functools.cached_property`.

### **Y332-DOUBLE-DISPATCH**
**Description:** Dynamic dispatch based on two objects' types.
**Example:** Visitor pattern implementation.

### **Y333-PLUGIN-ARCHITECTURE**
**Description:** Load and execute code dynamically.
**Example:** Parser plugins discovered via entry points.

### **Y334-ACTIVE-RECORD**
**Description:** Object wraps database row with data access methods.
**Example:** `transaction.save()`, `transaction.delete()`.
**Pragmatic:** Prefer repository pattern for better testability (Y323).
