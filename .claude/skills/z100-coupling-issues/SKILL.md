---
name: z100-coupling-issues
description: Python coupling anti-patterns (Z100-Z114). Use when reviewing code for tight coupling, circular dependencies, god objects, feature envy, or other coupling issues.
---

# Coupling Issues (Z100-Z114)

## 9. Coupling Issues (Z100-Z114)

### **Z100-TIGHT-COUPLING**
**Description:** Classes/modules directly depend on concrete implementations.
**Why Bad:** Changes ripple through system, hard to test, inflexible.
**Better:** Y203-DEPENDENCY-INJECTION, Y204-DEPENDENCY-INVERSION, Y102-USE-PROTOCOLS

### **Z101-CIRCULAR-DEPS**
**Description:** Module A imports B, B imports A.
**Why Bad:** Import errors, unclear dependencies, fragile.
**Better:** Y211-CIRCULAR-IMPORTS, Y120-TYPE-CHECKING

### **Z102-GOD-OBJECTS**
**Description:** One class does everything.
**Why Bad:** Hard to understand, test, maintain. Violates SRP.
**Better:** Y200-SINGLE-RESPONSIBILITY, Y202-SEPARATION-OF-CONCERNS

### **Z103-FEATURE-ENVY**
**Description:** Method uses another class's data more than its own.
**Why Bad:** Wrong responsibility placement, tight coupling.
**Better:** Move method to the class it envies.

### **Z104-INAPPROPRIATE-INTIMACY**
**Description:** Classes know too much about each other's internals.
**Why Bad:** Breaks encapsulation, fragile to changes.
**Better:** Y201-INTERFACE-SEGREGATION, Y222-FACADE-PATTERN

### **Z105-MESSAGE-CHAINS**
**Description:** Long chains like `a.b.c.d.e()`.
**Why Bad:** Fragile, violates Law of Demeter.
**Better:** Add methods to intermediate objects.

### **Z106-MIDDLE-MAN**
**Description:** Class just delegates to another class.
**Why Bad:** Unnecessary indirection.
**Better:** Remove middle man or give it real responsibility.

### **Z107-DATA-CLUMPS**
**Description:** Same group of parameters passed together everywhere.
**Why Bad:** Should be an object.
**Better:** Y112-DATACLASS-TYPES, Y114-NAMEDTUPLE-TYPES

### **Z108-PRIMITIVE-OBSESSION**
**Description:** Using primitives instead of small objects.
**Why Bad:** Loses type safety, business meaning.
**Better:** Y105-NEWTYPE, Y112-DATACLASS-TYPES

### **Z109-SHOTGUN-SURGERY**
**Description:** Single change requires modifying many classes.
**Why Bad:** Error-prone, indicates poor design.
**Better:** Y200-SINGLE-RESPONSIBILITY, Y213-COHESION

### **Z110-DIVERGENT-CHANGE**
**Description:** Class changes for multiple different reasons.
**Why Bad:** Violates SRP, hard to maintain.
**Better:** Y200-SINGLE-RESPONSIBILITY

### **Z111-REFUSED-BEQUEST**
**Description:** Subclass doesn't use parent's methods.
**Why Bad:** Wrong inheritance hierarchy.
**Better:** Y223-COMPOSITION-OVER-INHERITANCE

### **Z112-PARALLEL-INHERITANCE**
**Description:** Adding subclass in one hierarchy requires adding in another.
**Why Bad:** Maintenance burden, duplication.
**Better:** Y223-COMPOSITION-OVER-INHERITANCE

### **Z113-SPECULATIVE-GENERALITY**
**Description:** Code for future features that aren't needed yet.
**Why Bad:** Complexity without benefit, YAGNI violation.
**Better:** Build what you need now.

### **Z114-TEMPORARY-FIELD**
**Description:** Instance variable only used in some methods.
**Why Bad:** Confusing, suggests wrong abstraction.
**Better:** Pass as parameter or extract class.
