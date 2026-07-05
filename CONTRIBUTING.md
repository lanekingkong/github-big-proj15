# Contributing to OmniForge

Thank you for considering contributing to OmniForge! This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs
- Check if the bug has already been reported in [Issues](https://github.com/lanekingkong/omniforge/issues)
- Use the bug report template
- Include steps to reproduce, expected behavior, and actual behavior

### Suggesting Enhancements
- Check if the enhancement has already been suggested
- Use the feature request template
- Explain why this enhancement would be useful

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

## Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/omniforge.git
cd omniforge
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e ".[dev]"
pre-commit install
```

### 4. Run Tests
```bash
pytest tests/ -v
```

## Development Workflow

### Pre-commit Hooks
We use pre-commit hooks to ensure code quality:
- Black code formatting
- Ruff linting
- MyPy type checking
- End-of-file fixer
- Trailing whitespace trimmer

### Testing
- Write tests for all new functionality
- Maintain >90% test coverage
- Use pytest fixtures for complex setup
- Mock external dependencies

### Documentation
- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md

## Skill Development

### Creating New Skills
1. Create a new directory in `omniforge/skills/builtin/`
2. Add a `SKILL.md` file with proper frontmatter
3. Follow the skill template structure
4. Add examples and clear instructions
5. Test the skill thoroughly

### Skill Template
```markdown
---
name: skill-name
version: 1.0.0
author: Your Name
description: Brief description
tags: [tag1, tag2]
category: engineering
platforms: [claude-code, cursor]
---

# Skill Name

## Purpose
What does this skill do?

## When to Use
- When scenario 1
- When scenario 2

## Instructions
Step-by-step instructions...

## Examples
### Example 1
**Input**: Description
**Output**: Expected result
```

## Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all functions
- Document public APIs with docstrings
- Keep functions focused and small

### Imports
```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party
import yaml
from sqlite_utils import Database

# Local
from omniforge.core.engine import OmniForgeEngine
```

### Naming
- Classes: `CamelCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add new skill registry
fix: resolve memory leak in context optimizer
docs: update installation instructions
test: add tests for code understander
chore: update dependencies
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build and test distribution
6. Create GitHub release
7. Publish to PyPI

## Questions?

- Join our [Discussions](https://github.com/lanekingkong/omniforge/discussions)
- Check the [Documentation](https://docs.omniforge.dev)
- Email: dev@omniforge.dev

Thank you for contributing to OmniForge!