---
name: y500-documentation
description: Python documentation and readability guidelines (Y500-Y524). Use when writing docstrings, choosing variable names, formatting code, or adding comments to Python code.
---

# Documentation & Readability (Y500-Y524)

## 5. Documentation & Readability (Y500-Y524)

### **Y500-RST-DOCSTRINGS**
**Description:** Use reStructuredText format for docstrings.
**Example:**
```python
def parse(text: str) -> Transaction:
    """Parse transaction from text.

    :param text: Transaction text to parse
    :return: Parsed transaction object
    :raises ValueError: If text is invalid
    """
```
**Tool Support:** Sphinx uses RST docstrings.

### **Y501-DOCSTRING-COVERAGE**
**Description:** Document all public functions, classes, modules.
**Example:** Every `def` in public API has docstring.
**Tool Support:** ruff D100-D107 (some relaxed in pyproject.toml).

### **Y502-MODULE-DOCSTRINGS**
**Description:** Every module has docstring explaining its purpose.
**Example:** `"""VISA statement parser module."""` at top of file.

### **Y503-ONE-LINE-SUMMARY**
**Description:** First line of docstring is brief summary, then blank line, then details.
**Example:** `"""Parse transaction.\n\nDetailed description here..."""`

### **Y504-EXPRESSIVE-NAMES**
**Description:** Use clear, descriptive names. Avoid abbreviations.
**Example:** `transaction_parser` not `txn_prs`.
**Pragmatic:** Common abbrevs OK: `txn`, `df`, `ctx`.

### **Y505-VERB-FUNCTIONS**
**Description:** Function names start with verbs: `parse`, `calculate`, `validate`.
**Example:** `parse_transaction()` not `transaction()`.

### **Y506-NOUN-CLASSES**
**Description:** Class names are nouns: `Transaction`, `Parser`, `Validator`.
**Example:** `TransactionParser` not `ParseTransaction`.

### **Y507-BOOL-NAMING**
**Description:** Boolean variables/functions use `is_`, `has_`, `can_` prefix.
**Example:** `is_valid`, `has_errors`, `can_parse`.

### **Y508-COMMENT-WHY-NOT-WHAT**
**Description:** Comments explain *why*, not *what* (code shows what).
**Example:** `# Use Decimal to avoid float precision errors` not `# Create Decimal`.

### **Y509-REMOVE-DEAD-CODE**
**Description:** Delete commented-out code. Use version control.
**Example:** Don't keep `# old_function()` commented out.

### **Y510-TODO-COMMENTS**
**Description:** Use `# TODO: description` for temporary markers.
**Example:** `# TODO: Handle edge case when amount is zero`.
**Pragmatic:** Reference issue numbers: `# TODO(#123): Fix this`.

### **Y511-TYPE-HINTS-AS-DOCS**
**Description:** Type hints document expected types; don't repeat in docstring.
**Example:** Don't write `:param text: str - the text` when signature has `text: str`.

### **Y512-EXAMPLES-IN-DOCSTRINGS**
**Description:** Include usage examples in docstrings for complex functions.
**Example:**
```python
"""Parse amount.

Example:
    >>> parse_amount("$1,234.56")
    Decimal('1234.56')
"""
```

### **Y513-LINE-LENGTH**
**Description:** Max 88 characters per line (Black standard).
**Tool Support:** ruff E501 (relaxed for notebooks in pyproject.toml).
**Related:** Y210-IMPORT-ORDER

### **Y514-BLANK-LINES**
**Description:** Two blank lines between top-level definitions, one within classes.
**Tool Support:** ruff E301-E306 enforce.

### **Y515-INDENTATION**
**Description:** 4 spaces per indentation level.
**Tool Support:** ruff enforces via formatter.

### **Y516-CONSTANTS-NAMING**
**Description:** Constants use `UPPER_CASE_WITH_UNDERSCORES`.
**Example:** `MAX_RETRIES`, `DEFAULT_TIMEOUT`.
**Related:** Y108-FINAL

### **Y517-PRIVATE-NAMING**
**Description:** Private attributes/methods start with underscore.
**Example:** `_internal_cache`, `_validate_data()`.

### **Y518-DOUBLE-UNDERSCORE**
**Description:** Avoid `__name__` (dunder) unless implementing protocols.
**Example:** `__init__`, `__str__` OK. Don't use `__my_var` for privacy (use single `_`).

### **Y519-SELF-DOCUMENTING**
**Description:** Write code that explains itself. Reduce need for comments.
**Example:** `is_valid_transaction()` better than `check()` with comment explaining what it checks.

### **Y520-MAGIC-NUMBERS**
**Description:** Extract magic numbers to named constants.
**Example:** `TAX_RATE = 0.19; tax = amount * TAX_RATE` not `tax = amount * 0.19`.
**Pragmatic:** PLR2004 ignored in pyproject.toml for simple cases.

### **Y521-STRING-QUOTES**
**Description:** Consistent quote style. Double quotes `"` preferred.
**Tool Support:** ruff formatter enforces consistent quotes.

### **Y522-F-STRINGS**
**Description:** Use f-strings for formatting, not `%` or `.format()`.
**Example:** `f"{name}: {amount}"` not `"%s: %s" % (name, amount)`.

### **Y523-STRING-CONCATENATION**
**Description:** Use f-strings or `str.join()`, not `+` in loops.
**Example:** `"".join(parts)` not `s = ""; for p in parts: s += p`.
**Related:** Y805-STRING-PERFORMANCE

### **Y524-ASSERTION-MESSAGES**
**Description:** Include message in assertions explaining what failed.
**Example:** `assert amount > 0, f"Amount must be positive, got {amount}"`.
**Pragmatic:** S101 ignored for tests in pyproject.toml.
