---
name: y700-testing
description: Python testing guidelines (Y700-Y714). Use when writing tests, creating fixtures, using pytest parametrize, mocking dependencies, or applying TDD practices.
---

# Testing (Y700-Y714)

## 7. Testing (Y700-Y714)

### **Y700-TEST-NAMING**
**Description:** Test names describe what they test: `test_<what>_<condition>_<expected>`.
**Example:** `test_parse_invalid_date_raises_error`.

### **Y701-AAA-PATTERN**
**Description:** Tests follow Arrange-Act-Assert pattern.
**Example:**
```python
def test_parse():
    # Arrange
    text = "2025-01-15,100.00"
    # Act
    result = parse(text)
    # Assert
    assert result.amount == Decimal("100.00")
```

### **Y702-ONE-ASSERT-CONCEPT**
**Description:** Each test verifies one concept (multiple asserts OK if related).
**Example:** Test amount parsing separately from date parsing.

### **Y703-FIXTURES**
**Description:** Use pytest fixtures for reusable test data/setup.
**Example:** `@pytest.fixture; def sample_transaction(): return Transaction(...)`.

### **Y704-PARAMETRIZE**
**Description:** Use `@pytest.mark.parametrize` for testing multiple inputs.
**Example:** `@pytest.mark.parametrize("amount,expected", [(10, 11), (20, 22)])`.

### **Y705-MOCKING**
**Description:** Mock external dependencies (APIs, databases), not internal logic.
**Example:** `@patch('requests.get')` for HTTP calls.
**Pragmatic:** Don't over-mock; prefer real objects when simple.

### **Y706-TEST-COVERAGE**
**Description:** Aim for high coverage of business logic (80%+).
**Tool Support:** pytest-cov measures coverage.

### **Y707-INTEGRATION-TESTS**
**Description:** Test full workflows, not just units.
**Example:** Test parser + producer pipeline end-to-end.

### **Y708-TEST-DATA**
**Description:** Use realistic test data, include edge cases.
**Example:** Test with empty strings, max values, negative numbers, etc.

### **Y709-ISOLATION**
**Description:** Tests should be independent, runnable in any order.
**Example:** Don't rely on state from previous tests.

### **Y710-FAST-TESTS**
**Description:** Unit tests should be fast (<1s each).
**Example:** Use mocks for slow operations (network, disk).

### **Y711-TEST-HELPERS**
**Description:** Extract common test utilities to helper functions/fixtures.
**Example:** `make_transaction()` factory for tests.

### **Y712-DOCTEST**
**Description:** Use doctests for simple examples in docstrings.
**Example:** `>>> parse_amount("$10")` in docstring.
**Related:** Y512-EXAMPLES-IN-DOCSTRINGS

### **Y713-PROPERTY-TESTING**
**Description:** Consider property-based testing with hypothesis for complex logic.
**Example:** `@given(st.integers())` generates test inputs automatically.

### **Y714-TDD**
**Description:** Write tests before implementation (Test-Driven Development).
**Example:** Red (failing test) → Green (make it pass) → Refactor.
