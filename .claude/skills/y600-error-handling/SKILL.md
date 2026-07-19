---
name: y600-error-handling
description: Python error handling guidelines (Y600-Y614). Use when implementing exception handling, creating custom exceptions, using context managers, or designing error flows.
---

# Error Handling (Y600-Y614)

## 6. Error Handling (Y600-Y614)

### **Y600-SPECIFIC-EXCEPTIONS**
**Description:** Catch specific exceptions, not bare `except:`.
**Example:** `except ValueError:` not `except:`.
**Tool Support:** ruff E722 warns on bare except.

### **Y601-EXCEPTION-HIERARCHY**
**Description:** Create exception hierarchy for your domain.
**Example:** `class ParsingError(ValueError): ...` then `class VisaParsingError(ParsingError): ...`.

### **Y602-RAISE-FROM**
**Description:** Use `raise ... from ...` to preserve exception chain.
**Example:** `raise ValidationError(msg) from exc` preserves original exception.

### **Y603-CONTEXT-MANAGERS**
**Description:** Use context managers (`with`) for resource management.
**Example:** `with open(file) as f:` ensures file closes.
**Tool Support:** `contextlib` module for custom context managers.

### **Y604-SUPPRESS-EXCEPTIONS**
**Description:** Use `contextlib.suppress()` for expected exceptions to ignore.
**Example:** `with suppress(FileNotFoundError): os.remove(path)`.

### **Y605-FINALLY-CLEANUP**
**Description:** Use `finally` for cleanup that must happen regardless of exceptions.
**Example:** `try: ... finally: cleanup()`.

### **Y606-ELSE-CLAUSE**
**Description:** Use `else` in try/except for code that runs only if no exception.
**Example:** `try: data = parse() except: handle() else: process(data)`.

### **Y607-CUSTOM-EXCEPTIONS**
**Description:** Define custom exceptions for your domain errors.
**Example:** `class InsufficientFundsError(Exception): ...`.
**Related:** Y601-EXCEPTION-HIERARCHY

### **Y608-EXCEPTION-ARGS**
**Description:** Pass useful information to exceptions.
**Example:** `raise ValueError(f"Amount must be positive, got {amount}")`.

### **Y609-DONT-CATCH-ALL**
**Description:** Don't catch `BaseException` or `Exception` at top level unless re-raising.
**Example:** Only catch specific expected exceptions.

### **Y610-LOGGING-EXCEPTIONS**
**Description:** Log exceptions with context before re-raising or handling.
**Example:** `logger.exception("Failed to parse transaction %s", txn_id)`.

### **Y611-ASSERT-FOR-BUGS**
**Description:** Use assertions for impossible conditions (bugs), exceptions for expected errors.
**Example:** `assert parser is not None, "Parser must be set"` for internal invariants.
**Pragmatic:** S101 ignored in tests.

### **Y612-VALIDATION-EXCEPTIONS**
**Description:** Validate inputs and raise exceptions early.
**Example:** `if amount < 0: raise ValueError("Amount must be non-negative")`.

### **Y613-ERROR-MESSAGES**
**Description:** Error messages should be clear, actionable, include context.
**Example:** `f"Failed to parse date '{date_str}' with format '{fmt}'"` not `"Parse error"`.

### **Y614-EXITSTACK**
**Description:** Use `ExitStack` for dynamic number of context managers.
**Example:** `with ExitStack() as stack: files = [stack.enter_context(open(f)) for f in paths]`.
