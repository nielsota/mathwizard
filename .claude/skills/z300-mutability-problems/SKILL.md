---
name: z300-mutability-problems
description: Python mutability anti-patterns (Z300-Z314). Use when reviewing code for argument mutation, global state, mutable class attributes, or other mutability issues.
---

# Mutability Problems (Z300-Z314)

## 11. Mutability Problems (Z300-Z314)

### **Z300-MUTATING-ARGUMENTS**
**Description:** Function modifies its arguments.
**Why Bad:** Unexpected side effects, hard to reason about.
**Better:** Y403-AVOID-SIDE-EFFECTS, Y404-RETURN-NEW-VALUES

### **Z301-GLOBAL-STATE**
**Description:** Functions read/write global variables.
**Why Bad:** Hard to test, order-dependent, not thread-safe.
**Better:** Y420-AVOID-GLOBALS, Y203-DEPENDENCY-INJECTION

### **Z302-MUTABLE-CLASS-ATTRIBUTES**
**Description:** Mutable class variable shared across instances.
**Example:** `class Foo: items = []`  # shared!
**Why Bad:** Instances unexpectedly share state.
**Better:** Initialize in `__init__`.

### **Z303-SHARED-MUTABLE-REFS**
**Description:** Multiple references to same mutable object.
**Why Bad:** Modifications affect all references, hard to track.
**Better:** Y400-IMMUTABILITY, copy when needed.

### **Z304-MUTATING-DURING-ITERATION**
**Description:** Modifying collection while iterating.
**Example:** `for x in items: items.remove(x)`
**Why Bad:** Runtime error or undefined behavior.
**Better:** Iterate over copy or collect items to remove.

### **Z305-PROPERTY-WITH-SIDE-EFFECTS**
**Description:** Property getter that modifies state or does I/O.
**Why Bad:** Violates expectations (properties should be cheap, pure).
**Better:** Use method, not property.

### **Z306-MUTABLE-RETURN-INTERNAL**
**Description:** Returning mutable internal state.
**Example:** `return self._items` (list)
**Why Bad:** Caller can modify your internal state.
**Better:** Return copy or immutable view.

### **Z307-MODIFYING-CONSTANTS**
**Description:** Changing values marked as constants.
**Why Bad:** Breaks expectations, hard to debug.
**Better:** Y108-FINAL enforces immutability.

### **Z308-SINGLETON-MUTABLE-STATE**
**Description:** Singleton with mutable state.
**Why Bad:** Global mutable state, testing nightmare.
**Better:** Y303-SINGLETON-PATTERN used carefully or avoid.

### **Z309-CACHING-MUTABLE**
**Description:** Caching mutable objects.
**Why Bad:** Cached object modified, stale cache.
**Better:** Cache immutable data or deep copy.

### **Z310-MUTATING-LOOP-VARIABLE**
**Description:** Modifying loop variable inside loop.
**Example:** `for i in range(10): i += 1`  # doesn't work as expected
**Why Bad:** Confusing, doesn't affect loop.
**Better:** Use different variable.

### **Z311-DEFAULT-DICT-MUTATION**
**Description:** Mutating default dict values.
**Why Bad:** Unexpected sharing.
**Better:** Y413-AVOID-MUTABLE-DEFAULTS

### **Z312-IN-PLACE-OPERATIONS**
**Description:** `list.sort()` instead of `sorted(list)`.
**Why Bad:** Mutates original, can't chain.
**Better:** Use non-mutating versions when possible.
**Pragmatic:** In-place OK for performance when intentional.

### **Z313-FROZEN-VIOLATION**
**Description:** Working around frozen dataclass.
**Example:** `object.__setattr__(frozen_obj, 'x', value)`
**Why Bad:** Defeats immutability guarantees.
**Better:** Create new instance with Y412-DATACLASS-REPLACE.

### **Z314-MUTABLE-DATACLASS**
**Description:** Dataclass without `frozen=True` when should be immutable.
**Why Bad:** Accidental mutations, harder to reason about.
**Better:** Y401-FROZEN-DATACLASSES
