---
name: project-bootstrap
version: 1.0.0
author: OmniForge
description: Bootstrap new projects with best-practice scaffolding
tags: [scaffolding, bootstrap, starter, template, project-setup]
category: engineering
platforms: [claude-code, cursor, codex]
---

# Project Bootstrap Skill

## Purpose
Quickly scaffold new projects with best-practice structure, tooling, and configuration.

## When to Use
- Starting new Python projects
- Creating new npm packages
- Setting up monorepo structures
- Bootstrapping microservices

## Instructions

### 1. Project Structure (Python)
```
project/
├── src/project_name/
│   ├── __init__.py
│   ├── core/
│   ├── utils/
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core/
├── docs/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
└── Makefile
```

### 2. Required Tooling
- **Linting**: ruff (Python) / eslint (JS)
- **Formatting**: black / prettier
- **Testing**: pytest / jest
- **Type checking**: mypy / TypeScript
- **Pre-commit hooks**: Standard checks
- **CI**: GitHub Actions template

### 3. Quality Gates
- pyproject.toml with all tool configs
- .gitignore with language-specific ignores
- Pre-commit hooks configured
- CI pipeline ready
- README with badges

## Output
Generated project scaffold ready for development.