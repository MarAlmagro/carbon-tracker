# Architecture Overview

## System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS                                   │
│  (Browser / Mobile / AI Agents)                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   React     │ │  REST API   │ │    MCP      │
    │    SPA      │ │  /api/v1/   │ │   Server    │
    │  (Vercel)   │ │  (Render)   │ │  (Render)   │
    └─────────────┘ └──────┬──────┘ └──────┬──────┘
                           │               │
                           └───────┬───────┘
                                   │
                           ┌───────▼───────┐
                           │   Supabase    │
                           │  PostgreSQL   │
                           │    + Auth     │
                           └───────────────┘
```

## Hexagonal Architecture

### Why Hexagonal?
- Clear separation between business logic and external concerns
- Easy to test domain logic in isolation
- Multiple adapters can share same domain (REST API + MCP)
- Demonstrates architectural maturity for portfolio

### Layer Responsibilities

#### Domain (Core)
Location: `backend/src/domain/`

Contains pure business logic with no external dependencies.

```
domain/
├── entities/           # Business objects
│   ├── activity.py    # Activity entity (transport, energy, food)
│   ├── user.py        # User entity (optional account)
│   ├── emission_factor.py
│   └── footprint.py   # Calculated footprint
│
├── services/          # Business operations
│   ├── calculation_service.py  # CO2e calculations
│   ├── comparison_service.py   # Regional comparisons
│   └── aggregation_service.py  # Time-based aggregations
│
├── ports/             # Interfaces (abstract base classes)
│   ├── activity_repository.py
│   ├── user_repository.py
│   ├── emission_factor_repository.py
│   └── region_data_provider.py
│
└── use_cases/         # Application use cases
    ├── log_activity.py
    ├── get_footprint_summary.py
    └── compare_to_region.py
```

#### API Adapter (Driving/Primary)
Location: `backend/src/api/`

HTTP interface that drives the application.

```
api/
├── routes/
│   ├── activities.py   # POST /activities, GET /activities
│   ├── footprint.py    # GET /footprint/summary
│   ├── comparison.py   # GET /comparison/region
│   └── health.py       # GET /health
│
├── middleware/
│   ├── cors.py
│   ├── rate_limit.py
│   └── error_handler.py
│
├── dependencies/
│   ├── auth.py         # Supabase JWT validation
│   └── db.py           # Database session
│
└── schemas/            # Pydantic request/response models
    └── (generated from OpenAPI)
```

#### Infrastructure Adapters (Driven/Secondary)
Location: `backend/src/infrastructure/`

Implementations of domain ports.

```
infrastructure/
├── repositories/       # Database implementations
│   ├── supabase_activity_repo.py
│   ├── supabase_user_repo.py
│   └── supabase_emission_factor_repo.py
│
├── external/          # External service integrations
│   ├── supabase_auth.py
│   └── ip_geolocation.py
│
└── config/
    ├── settings.py    # Pydantic settings
    └── supabase.py    # Supabase client setup
```

#### MCP Adapter
Location: `backend/src/mcp/`

Exposes domain operations to AI agents.

```
mcp/
├── server.py          # MCP server setup
├── tools/
│   ├── log_activity.py
│   ├── get_footprint.py
│   └── compare_region.py
└── schemas.py         # MCP input/output schemas
```

### Dependency Rule

```
    External World
         │
         ▼
┌─────────────────┐
│    Adapters     │  ← Depends on Domain
│  (API, MCP, DB) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Domain      │  ← No external dependencies
│  (Pure Python)  │
└─────────────────┘
```

**Rule:** Dependencies point inward. Domain never imports from adapters.

### Dependency Injection

Use cases receive ports via constructor injection:

```python
# domain/use_cases/log_activity.py
class LogActivityUseCase:
    def __init__(
        self,
        activity_repo: ActivityRepository,  # Port (interface)
        emission_factor_repo: EmissionFactorRepository,
        calculation_service: CalculationService
    ):
        self._activity_repo = activity_repo
        self._emission_factor_repo = emission_factor_repo
        self._calculation_service = calculation_service

    async def execute(self, activity_data: ActivityInput) -> Activity:
        factor = await self._emission_factor_repo.get_by_type(
            activity_data.activity_type
        )
        co2e = self._calculation_service.calculate(activity_data, factor)
        activity = Activity(
            **activity_data.dict(),
            co2e_kg=co2e
        )
        return await self._activity_repo.save(activity)
```

```python
# api/dependencies/use_cases.py
def get_log_activity_use_case(
    client: Client = Depends(get_supabase_client)
) -> LogActivityUseCase:
    return LogActivityUseCase(
        activity_repo=SupabaseActivityRepository(client),  # Adapter
        emission_factor_repo=SupabaseEmissionFactorRepository(client),
        calculation_service=CalculationService()
    )
```

## Frontend Architecture

```
frontend/src/
├── components/
│   ├── ui/              # Reusable UI primitives (shadcn)
│   ├── features/        # Feature-specific components
│   │   ├── activity/    # Activity logging
│   │   ├── dashboard/   # Charts and summary
│   │   └── comparison/  # Regional comparison
│   └── layout/          # App shell, navigation
│
├── hooks/               # Custom hooks
│   ├── useActivities.ts
│   ├── useFootprint.ts
│   └── useAuth.ts
│
├── services/            # API client (generated from OpenAPI)
│   └── api.ts
│
├── store/               # Zustand stores
│   ├── activityStore.ts
│   └── authStore.ts
│
├── i18n/
│   ├── index.ts         # i18next setup
│   └── locales/
│       ├── en.json
│       └── es.json
│
└── types/               # Generated from OpenAPI
    └── api.d.ts
```

## Data Flow Example: Log Activity

```
┌──────────┐   POST /activities    ┌──────────────┐
│  React   │ ───────────────────► │   FastAPI    │
│   SPA    │                       │   Router     │
└──────────┘                       └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  Use Case    │
                                   │ LogActivity  │
                                   └──────┬───────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
            ┌──────────────┐     ┌──────────────┐      ┌──────────────┐
            │EmissionFactor│     │ Calculation  │      │  Activity    │
            │  Repository  │     │   Service    │      │  Repository  │
            └──────────────┘     └──────────────┘      └──────────────┘
                    │                                          │
                    └──────────────────────────────────────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  PostgreSQL  │
                                   │  (Supabase)  │
                                   └──────────────┘
```

## API Versioning Strategy

- Base path: `/api/v1/`
- Breaking changes: New version (`/api/v2/`)
- Non-breaking additions: Same version
- Deprecation: 3-month notice in headers

## Security Layers

1. **CORS** - Whitelist frontend origins
2. **Rate Limiting** - Per IP, stricter for anonymous
3. **Input Validation** - Pydantic schemas
4. **Authentication** - Supabase JWT (optional)
5. **Authorization** - User can only access own data
