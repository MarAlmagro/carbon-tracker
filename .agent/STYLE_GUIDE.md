# Style Guide

This guide provides high-level coding conventions. For detailed rules, see the specific rule files:

- **[rules/python.md](rules/python.md)** - Python coding standards
- **[rules/react.md](rules/react.md)** - React/TypeScript standards  
- **[rules/git.md](rules/git.md)** - Git commit conventions
- **[rules/error-handling.md](rules/error-handling.md)** - Error handling patterns

## Quick Reference

### Python (Backend)
- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Type checker**: mypy (strict mode)
- **Style**: Type hints required, Pydantic for validation
- **Async**: Use for all I/O operations

### TypeScript (Frontend)
- **Mode**: Strict TypeScript
- **Components**: Functional only
- **Styling**: Tailwind CSS, mobile-first
- **Testing**: data-testid for E2E tests
- **State**: Zustand for global state

### Git
- **Branches**: `feature/CT-XXX-description`
- **Commits**: Conventional format (`feat:`, `fix:`, `docs:`)
- **PR**: Always to `develop`
