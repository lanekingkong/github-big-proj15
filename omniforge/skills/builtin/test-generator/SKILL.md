---
name: test-generator
version: 1.0.0
author: OmniForge
description: Generate comprehensive test suites with coverage goals
tags: [testing, unittest, pytest, coverage]
category: engineering
platforms: [claude-code, cursor, codex, copilot]
---

# Test Generator Skill

## Purpose
Generate thorough test suites with >90% coverage goals, property-based testing, and edge case coverage.

## When to Use
- Creating test suites for new code
- Improving existing test coverage
- Adding property-based tests
- Generating edge case tests
- Setting up CI test pipelines

## Instructions

### 1. Test Types to Generate
- **Unit tests**: Individual function/class behavior
- **Integration tests**: Module interaction
- **Property-based tests**: Invariants that always hold
- **Edge cases**: Boundary values, empty inputs, special characters
- **Error cases**: Invalid inputs, network failures, timeouts
- **Performance tests**: Benchmarks for critical paths

### 2. Test Coverage Targets
- Core logic: 100%
- Business rules: 100%
- Utility functions: 95%
- UI components: 80%
- Overall project: >90%

### 3. Testing Patterns
```python
# Arrange-Act-Assert
def test_function():
    # Arrange
    data = prepare_test_data()
    # Act
    result = function_under_test(data)
    # Assert
    assert result == expected

# Parametrized tests
@pytest.mark.parametrize("input,expected", [
    (1, True),
    (0, False),
    (-1, False),
])
def test_validation(input, expected):
    assert validate(input) == expected
```

### 4. Anti-Patterns to Avoid
- Testing implementation details instead of behavior
- Tests that depend on execution order
- Sleep-based timing tests
- Hard-coded external service dependencies
- Tests without assertions

## Output Format
Generate complete test files with proper imports, fixtures, and documentation.