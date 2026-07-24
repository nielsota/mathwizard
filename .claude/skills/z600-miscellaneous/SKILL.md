---
name: z600-miscellaneous
description: Miscellaneous Python anti-patterns (Z600-Z604). Use when reviewing code for magic numbers, deep nesting, long functions, inconsistent naming, or commented-out code.
---

# Miscellaneous (Z600-Z604)

## 14. Miscellaneous (Z600-Z9999)

### **Z600-MAGIC-NUMBERS**
**Description:** Unexplained constants in code.
**Example:** `if age > 65:` what's 65?
**Why Bad:** Unclear meaning, hard to maintain.
**Better:** Y520-MAGIC-NUMBERS with named constants.
**Pragmatic:** PLR2004 ignored for truly obvious cases.

### **Z601-DEEP-NESTING**
**Description:** Code nested 5+ levels deep.
**Why Bad:** Hard to read, understand.
**Better:** Y808-EARLY-RETURN, extract functions.

### **Z602-LONG-FUNCTIONS**
**Description:** Functions > 50 lines.
**Why Bad:** Hard to understand, test, reuse.
**Better:** Extract smaller functions.

### **Z603-INCONSISTENT-NAMING**
**Description:** Similar things named differently.
**Example:** `get_user`, `fetch_transaction`, `retrieve_account`
**Why Bad:** Confusing, hard to remember.
**Better:** Y504-EXPRESSIVE-NAMES consistently.

### **Z604-COMMENTED-OUT-CODE**
**Description:** Old code left commented out.
**Why Bad:** Clutter, confusion about whether to use.
**Better:** Y509-REMOVE-DEAD-CODE, use version control.
