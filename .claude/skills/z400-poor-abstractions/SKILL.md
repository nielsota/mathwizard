---
name: z400-poor-abstractions
description: Python abstraction anti-patterns (Z400-Z409). Use when reviewing code for leaky abstractions, wrong abstraction levels, long parameter lists, or boolean flag arguments.
---

# Poor Abstractions (Z400-Z409)

## 12. Poor Abstractions (Z400-Z409)

### **Z400-LEAKY-ABSTRACTION**
**Description:** Implementation details leak through interface.
**Why Bad:** Users coupled to internals, defeats abstraction.
**Better:** Hide implementation, stable interface.

### **Z401-WRONG-ABSTRACTION-LEVEL**
**Description:** Mixing high and low-level concepts.
**Example:** Business logic mixed with SQL queries.
**Why Bad:** Hard to understand, change, test.
**Better:** Y202-SEPARATION-OF-CONCERNS

### **Z402-PREMATURE-ABSTRACTION**
**Description:** Abstracting before patterns emerge.
**Why Bad:** Wrong abstraction is worse than duplication.
**Better:** Wait for 3rd use case (Rule of Three).

### **Z403-MISSING-ABSTRACTION**
**Description:** Duplicated code that should be abstracted.
**Why Bad:** Maintenance burden, inconsistency.
**Better:** Extract common code when pattern clear.

### **Z404-INCOMPLETE-ABSTRACTION**
**Description:** Abstraction doesn't cover all cases.
**Why Bad:** Special cases leak out.
**Better:** Rethink abstraction or accept limitations.

### **Z405-BOOLEAN-PARAMETERS**
**Description:** Function with boolean flag changing behavior.
**Example:** `def process(data, strict=True)`
**Why Bad:** Two functions in one, unclear at call site.
**Better:** Two functions or Y304-STRATEGY-PATTERN.

### **Z406-LONG-PARAMETER-LIST**
**Description:** Function with many parameters (>5).
**Why Bad:** Hard to remember, use, test.
**Better:** Y112-DATACLASS-TYPES for parameter object.

### **Z407-OUTPUT-PARAMETER**
**Description:** Modifying argument to return value.
**Example:** `def compute(input, output_list)` modifies `output_list`
**Why Bad:** Unclear, violates functional style.
**Better:** Return value explicitly.

### **Z408-FLAG-ARGUMENT**
**Description:** Boolean that completely changes function behavior.
**Why Bad:** Really two different functions.
**Better:** Split into two functions.

### **Z409-TRAIN-WRECK**
**Description:** Long method chains `a.b().c().d().e()`.
**Why Bad:** Tight coupling, fragile.
**Better:** Y222-FACADE-PATTERN or fewer levels.
