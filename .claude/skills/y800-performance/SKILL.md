---
name: y800-performance
description: Python performance and optimization guidelines (Y800-Y814). Use when optimizing code, profiling bottlenecks, choosing between generators and lists, or applying caching strategies.
---

# Performance & Best Practices (Y800-Y814)

## 8. Performance & Best Practices (Y800-Y9999)

### **Y800-PREMATURE-OPTIMIZATION**
**Description:** Don't optimize until you measure. Clarity first.
**Example:** Write clear code, profile to find bottlenecks, then optimize.

### **Y801-PROFILE-FIRST**
**Description:** Use profiler (cProfile, line_profiler) to find actual bottlenecks.
**Tool Support:** `python -m cProfile script.py`.

### **Y802-GENERATOR-VS-LIST**
**Description:** **Favor generators over lists by default.** Use generator expressions for large datasets to save memory and enable lazy evaluation. Only materialize to lists when you need random access, length, or multiple iterations.

**Default Choice:** Generator (lazy evaluation)
- Use `(x for x in items)` generator expression
- Return `Iterator[T]` from functions
- Let caller decide when/if to materialize with `list()`

**When List is Better:**
- Need to iterate multiple times over same data
- Need random access (`result[3]`)
- Need length without consuming (`len(result)`)
- Small datasets where memory isn't a concern
- Returning from public API where lazy evaluation complicates usage

**Examples:**

```python
from collections.abc import Iterator

# GOOD: Default to generator for transformations
def parse_file(path: Path) -> Iterator[Record]:
    """Parse records lazily - caller controls materialization."""
    with path.open() as f:
        for line in f:
            yield parse_line(line)

# Caller decides when to materialize
records = parse_file(path)
first_100 = list(itertools.islice(records, 100))  # Only parses 100 lines

# GOOD: Generator expression for filtering
large_txns = (txn for txn in transactions if txn.amount > 1000)

# BAD: List comprehension loads everything into memory
def parse_file(path: Path) -> list[Record]:
    with path.open() as f:
        return [parse_line(line) for line in f]  # All at once!

# BAD: Unnecessary list creation
large_txns = [txn for txn in transactions if txn.amount > 1000]
```

**Memory Impact:**
- List: O(n) memory for n items (all stored)
- Generator: O(1) memory (one item at a time)
- For 1M transactions: ~800MB (list) vs ~80 bytes (generator)

**Performance Impact:**
- Generator: Immediate start, incremental results
- List: Upfront delay to build entire list
- Generator wins when: processing streams, early termination, partial consumption

**Migration Pattern:**
When converting tuple/list returns to generators:
1. Change return type: `tuple[T, ...]` → `Iterator[T]`
2. Replace list building with `yield`
3. Update callers to use `list()` only where needed
4. Update tests to materialize before assertions

**Related:** Y405-GENERATORS, Y406-LAZY-EVALUATION, Y314-ITERATOR-PATTERN

### **Y803-DICT-LOOKUPS**
**Description:** Use dict lookups instead of long if/elif chains.
**Example:** `PARSERS = {"visa": VisaParser, ...}; Parser = PARSERS[type]`.

### **Y804-CACHING**
**Description:** Cache expensive computations with `@lru_cache` or `@cache`.
**Example:** `@lru_cache(maxsize=128); def expensive_func(): ...`.
**Related:** Y409-FUNCTOOLS

### **Y805-STRING-PERFORMANCE**
**Description:** Use `str.join()` for concatenating many strings.
**Example:** `"".join(parts)` faster than repeated `+` in loop.
**Related:** Y523-STRING-CONCATENATION

### **Y806-SLOTS**
**Description:** Use `__slots__` for memory optimization in classes with many instances.
**Example:** `class Point: __slots__ = ('x', 'y')`.
**Pragmatic:** Only when profiling shows memory issues.

### **Y807-LOCAL-LOOKUPS**
**Description:** Local variables faster than global/attribute lookups.
**Example:** `local_func = obj.method; for x in items: local_func(x)`.
**Pragmatic:** Only optimize hot loops after profiling.

### **Y808-EARLY-RETURN**
**Description:** Return early from functions to reduce nesting.
**Example:** `if error: return None; # rest of logic` not `if not error: # all logic`.

### **Y809-AVOID-DOTS**
**Description:** In hot loops, minimize attribute access.
**Example:** Cache `obj.attr` in local variable before loop.
**Pragmatic:** Only in performance-critical code.

### **Y810-BUILT-INS**
**Description:** Use built-in functions (C-optimized) when possible.
**Example:** `sum()`, `min()`, `max()` faster than manual loops.

### **Y811-NUMPY-PANDAS**
**Description:** For numerical data, use numpy/pandas (vectorized operations).
**Example:** `df['new_col'] = df['col'] * 2` faster than row-by-row.

### **Y812-COMPILE-REGEX**
**Description:** Compile regexes used repeatedly.
**Example:** `PATTERN = re.compile(r"..."); PATTERN.match(text)` not `re.match(r"...", text)` in loop.

### **Y813-SET-MEMBERSHIP**
**Description:** Use sets for membership testing (`in`), not lists.
**Example:** `ALLOWED = {"a", "b", "c"}; if x in ALLOWED` faster than list.

### **Y814-LAZY-IMPORTS**
**Description:** Import expensive modules only when needed.
**Example:** `def plot(): import matplotlib; ...` if matplotlib not always used.
**Related:** Y212-LAZY-IMPORTS
