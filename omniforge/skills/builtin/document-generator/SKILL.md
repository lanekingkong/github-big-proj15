---
name: document-generator
version: 1.0.0
author: OmniForge
description: Generate comprehensive project documentation
tags: [documentation, docs, readme, markdown]
category: engineering
platforms: [claude-code, cursor, codex]
---

# Document Generator Skill

## Purpose
Auto-generate comprehensive, production-quality documentation for any project.

## When to Use
- Creating README files
- Writing API documentation
- Generating architecture docs
- Building contributor guides

## Instructions

### 1. Documentation Types
Generate based on project needs:
- **README.md**: Project overview, installation, quick start
- **ARCHITECTURE.md**: System design, data flow, component diagram
- **API.md**: Endpoint documentation, examples
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history

### 2. README Template
```markdown
# [Project Name]
[Badge Section]

## Overview
[One paragraph description]

## Features
- Feature 1
- Feature 2

## Quick Start
### Prerequisites
### Installation
## Usage
## Configuration
## Documentation
## Contributing
## License
```

### 3. Quality Standards
- All commands copy-pasteable
- All examples tested
- Code blocks have language annotation
- Screenshots have alt text
- Links verified (no 404s)
- Consistent terminology

## Output
Generate complete, ready-to-publish documentation files.