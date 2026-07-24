---
name: z500-testing-antipatterns
description: Python testing anti-patterns (Z500-Z509). Use when reviewing test code for implementation coupling, brittle tests, over-mocking, or missing edge cases.
---

# Testing Anti-patterns (Z500-Z509)

## 13. Testing Anti-patterns (Z500-Z509)

### **Z500-TESTING-IMPLEMENTATION**
**Description:** Tests know too much about implementation details.
**Why Bad:** Brittle, refactoring breaks tests.
**Better:** Test behavior, not implementation.

### **Z501-BRITTLE-TESTS**
**Description:** Tests break on unrelated changes.
**Why Bad:** False negatives, maintenance burden.
**Better:** Y709-ISOLATION, test public interface.

### **Z502-TEST-INTERDEPENDENCE**
**Description:** Tests depend on each other, must run in order.
**Why Bad:** Can't run individually, hard to debug.
**Better:** Y709-ISOLATION

### **Z503-OVER-MOCKING**
**Description:** Mocking everything including internal logic.
**Why Bad:** Tests don't test real code.
**Better:** Y705-MOCKING only external dependencies.

### **Z504-MISSING-EDGE-CASES**
**Description:** Only happy path tested.
**Why Bad:** Bugs in error handling.
**Better:** Y708-TEST-DATA with edge cases.

### **Z505-SLOW-TESTS**
**Description:** Unit tests take minutes to run.
**Why Bad:** Developers don't run them.
**Better:** Y710-FAST-TESTS, use mocks.

### **Z506-TESTING-PRIVATE-METHODS**
**Description:** Tests call private methods directly.
**Why Bad:** Couples tests to implementation.
**Better:** Test through public interface.

### **Z507-ASSERTION-ROULETTE**
**Description:** Multiple unrelated asserts, unclear which failed.
**Why Bad:** Hard to debug failures.
**Better:** Y702-ONE-ASSERT-CONCEPT

### **Z508-TEST-CODE-IN-PRODUCTION**
**Description:** Test utilities, fixtures in production code.
**Why Bad:** Bloat, security risk.
**Better:** Separate test code.

### **Z509-IGNORING-FAILURES**
**Description:** Commented-out failing tests.
**Why Bad:** Technical debt, false confidence.
**Better:** Fix or remove tests.
