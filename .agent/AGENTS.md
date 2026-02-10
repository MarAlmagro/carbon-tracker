---
trigger: always_on
---

# Carbon Footprint Tracker - Agent Guide

## Project Overview

A web application for tracking personal carbon footprint with optional user accounts, regional comparisons, and AI agent integration via MCP.

**Tech Stack:**
- Backend: FastAPI + Supabase Python Client (supabase-py) + PostgreSQL (Supabase)
- Frontend: React 18 + TypeScript + Vite + Tailwind
- Architecture: Hexagonal (Ports & Adapters)
- API: OpenAPI-first development

## Quick Navigation

```
carbon-tracker/
├── backend/                # FastAPI application
│   ├── src/
│   │   ├── api/            # HTTP adapters (routes, middleware)
│   │   ├── domain/         # Business logic (entities, services, ports)
│   │   ├── infrastructure/ # External adapters (DB, external APIs)
│   │   └── mcp/            # MCP server module
│   └── tests/
├── frontend/               # React SPA
│   └── src/
│       ├── components/     # UI components
│       ├── hooks/          # Custom React hooks
│       ├── services/       # API client
│       ├── store/          # State management
│       └── i18n/           # Translations (en, es)
├── docs/
│   ├── api-contracts/      # OpenAPI specs (source of truth)
│   ├── adr/                # Architecture Decision Records
│   └── diagrams/           # System diagrams
├── scripts/                # Utility scripts
└── .agent/                 # Agent tooling (you are here)
│   ├── README.md            # Agent system overview
│   ├── DEVELOPMENT_SETUP.md # Local development setup
│   ├── TESTING_GUIDE.md     # Testing patterns & philosophy
│   ├── DEPLOYMENT.md        # Deployment procedures (TBD)
│   ├── MCP_SERVER.md        # MCP server documentation (TBD)
│   ├── specs/features/      # Feature specifications
│   ├── plans/               # Feature plans
│   ├── skills/              # Skills
│   ├── rules/               # Rules & standards
│   ├── commands/            # Command templates
│   ├── workflows/           # Workflows
│   ├── AGENTS.md            # This file
│   ├── ARCHITECTURE.md      # Architecture Overview
│   ├── STYLE_GUIDE.md       # Coding Style Guide (high-level)
│   └── FEATURE_PROGRESS.md  # Feature implementation tracking
```

## Architecture Overview

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Coding Standards

See [STYLE_GUIDE.md](STYLE_GUIDE.md) for high-level conventions.

### Detailed Rules
- **[rules/python.md](rules/python.md)** - Python coding standards
- **[rules/react.md](rules/react.md)** - React/TypeScript standards (includes mobile-first & E2E)
- **[rules/git.md](rules/git.md)** - Git commit conventions
- **[rules/error-handling.md](rules/error-handling.md)** - Error handling patterns

### Quick Reference
- **Python**: Type hints required, Pydantic for validation
- **TypeScript**: Strict mode, functional components only, mobile-first responsive design
- **Git**: Conventional commits, feature branches
- **i18n**: All user strings in translation files
- **Testing**: data-testid for E2E tests

## Domain Glossary

| Term | Definition |
|------|------------|
| CO2e | Carbon dioxide equivalent - standard unit for measuring carbon footprint |
| Emission Factor | Multiplier to convert activity (km, kWh) to CO2e |
| Activity | A logged user action (transport trip, energy usage, meal) |
| Footprint | Aggregated CO2e over a time period |
| Anonymous Session | User without account, data in localStorage |

## Working with This Codebase

### Before Starting Any Task
1. Read the relevant feature spec in `.agent/specs/features/`
2. Check `/docs/api-contracts/` for API definitions
3. Review related ADRs in `/docs/adr/`

### Feature Implementation Workflow
See [workflows/feature-branch.md](workflows/feature-branch.md) for detailed workflow.

### Testing Requirements
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing patterns.

### Quick Reference
- **Domain logic**: `/backend/src/domain/`
- **API endpoints**: `/backend/src/api/routes/`
- **Frontend components**: `/frontend/src/components/features/`

## Critical Rules

1. **Never commit secrets** - Use environment variables with placeholders
2. **OpenAPI is source of truth** - Generate types from spec
3. **Domain has no external dependencies** - Only ports (interfaces)
4. **All user input validated** - Pydantic (BE) + Zod (FE)
5. **i18n from start** - All user-facing strings in translation files

## Related Documentation

### Core Documentation
- [README.md](README.md) - Agent system overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system design
- [STYLE_GUIDE.md](STYLE_GUIDE.md) - Coding standards
- [FEATURE_PROGRESS.md](FEATURE_PROGRESS.md) - Feature implementation tracking

### Development Guides
- [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) - Local development setup
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing patterns and examples
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures (TBD)
- [MCP_SERVER.md](MCP_SERVER.md) - MCP server setup (TBD)

### Workflow & Specs
- [workflows/feature-branch.md](workflows/feature-branch.md) - Feature workflow
- [specs/features/](specs/features/) - Feature specifications
- [commands/](commands/) - Command templates

### Rules & Standards
- [rules/python.md](rules/python.md) - Python coding rules
- [rules/react.md](rules/react.md) - React/TypeScript rules (includes responsive design & E2E test conventions)
- [rules/git.md](rules/git.md) - Git commit conventions
- [rules/error-handling.md](rules/error-handling.md) - Error handling patterns

### External Documentation
- [docs/adr/](../docs/adr/) - Architecture Decision Records
- [docs/api-contracts/](../docs/api-contracts/) - OpenAPI specifications