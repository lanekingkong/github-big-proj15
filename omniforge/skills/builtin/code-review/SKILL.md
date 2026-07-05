---
name: code-review
version: 1.0.0
author: OmniForge
description: Production-grade code review skill with quality gates
tags: [code, review, quality, production]
category: engineering
platforms: [claude-code, cursor, codex, copilot]
---

# Code Review Skill

## Purpose
Perform thorough, production-grade code reviews with structured feedback.

## When to Use
- When reviewing pull requests
- When evaluating code quality
- When checking for security vulnerabilities
- When verifying against coding standards

## Instructions

### 1. Review Structure
- **Summary**: Brief overview of what the code does
- **Critical Issues**: Blocking problems (security, data loss, breakage)
- **Major Issues**: Non-blocking but important (architecture, performance)
- **Minor Issues**: Style, naming, documentation
- **Suggestions**: Optional improvements

### 2. Quality Gates
Every review must check:
- [ ] Security: No SQL injection, XSS, sensitive data exposure
- [ ] Error handling: All error paths covered
- [ ] Testing: Adequate test coverage
- [ ] Performance: No obvious bottlenecks
- [ ] Documentation: Self-documenting code
- [ ] Accessibility: WCAG 2.1 AA compliance (if applicable)

### 3. Anti-Patterns to Flag
- Magic numbers (extract to constants)
- Deep nesting (>3 levels)
- God functions/classes
- Premature optimization
- Commented-out code
- TODO markers without tickets

## Output Format

```markdown
## Code Review: [PR/File Name]

### Summary
[Brief summary]

### Critical Issues (must fix)
1. [Issue] — [Impact] — [Fix suggestion]

### Major Issues (should fix)
1. [Issue] — [Impact] — [Fix suggestion]

### Minor Issues (nice to fix)
1. [Issue] — [Fix suggestion]

### Suggestions
1. [Suggestion]

### Overall Assessment
- Security: ✅/⚠️/❌
- Quality: ✅/⚠️/❌
- Readiness: Ready / Needs work / Not ready
```