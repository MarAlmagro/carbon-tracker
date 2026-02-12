# Carbon Footprint Tracker

A web application for tracking personal carbon footprint with optional user accounts, regional comparisons, and AI agent integration.

## Features

- 🚗 Log transport activities (car, bus, train, bike)
- ⚡ Track home energy usage
- 🍽️ Monitor food-related emissions
- 📊 Dashboard with charts and trends
- 🌍 Compare your footprint to regional averages
- 🔐 Optional account creation (works anonymously too)
- 🤖 MCP server for AI agent integration
- 🌐 Multilingual (English, Spanish)

## Tech Stack

### Backend
- FastAPI + Pydantic v2
- Supabase Python Client (supabase-py) + PostgreSQL
- Hexagonal Architecture
- Supabase Auth + DB (schema managed via Supabase dashboard/SQL editor)

### Frontend
- React 18 + TypeScript
- Vite + Tailwind CSS
- React Query + Zustand
- i18next for translations

### DevOps
- Docker + Docker Compose
- GitHub Actions CI/CD
- Render (API) + Vercel (Frontend) + Supabase (DB)

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/carbon-tracker.git
cd carbon-tracker

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker compose up -d

# Access:
# - Frontend: http://localhost:5173
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Without Docker

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
carbon-tracker/
├── backend/           # FastAPI application
│   ├── src/
│   │   ├── api/       # HTTP routes
│   │   ├── domain/    # Business logic
│   │   └── infrastructure/  # DB, external services
│   └── tests/
├── frontend/          # React SPA
│   └── src/
├── docs/              # Documentation
│   ├── api-contracts/ # OpenAPI spec
│   └── adr/          # Architecture decisions
└── .agent/           # AI agent tooling
```

## Development

### Running Tests

```bash
# Backend
cd backend
pytest --cov

# Frontend
cd frontend
npm test
```

### Linting

```bash
# Backend
cd backend
ruff check .
mypy src

# Frontend
cd frontend
npm run lint
npm run typecheck
```

## Dashboard

The dashboard provides visual insights into your carbon footprint with interactive charts and period-based filtering.

### Features

- **Summary Card** — Total CO2e, activity count, % change vs previous period, daily average
- **Category Breakdown** — Pie chart showing emissions split by category (transport, energy, food)
- **Trend Chart** — Line chart showing daily emissions over the selected period
- **Period Selector** — Switch between Today, This Week, This Month, This Year, All Time

### API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/v1/footprint/summary?period=month` | Summary with totals and period comparison |
| `GET /api/v1/footprint/breakdown?period=month` | Category breakdown with percentages |
| `GET /api/v1/footprint/trend?period=month` | Daily time-series data points |

All endpoints accept `period` (`day`, `week`, `month`, `year`, `all`) and optional `start_date`/`end_date` query parameters. Authentication is via `Authorization: Bearer <token>` header (authenticated users) or `X-Session-ID` header (guests).

### Aggregation Logic

The backend aggregation service (`backend/src/domain/services/aggregation_service.py`) performs all calculations as pure business logic with no external dependencies:

- **Total CO2e** — Sums `co2e_kg` across all activities in the date range
- **Category Breakdown** — Groups activities by `category` field, sums CO2e per group, calculates percentage of total
- **Daily Trend** — Buckets activities by date, fills missing dates in the range with zero values to produce a continuous time series
- **Period Dates** — Converts period strings to `(start_date, end_date)` tuples:
  - `day` → today only
  - `week` → Monday to Sunday of current week
  - `month` → 1st to last day of current month
  - `year` → Jan 1 to Dec 31 of current year
  - `all` → 2020-01-01 to 2030-12-31
- **Period Comparison** — Fetches the equivalent previous period (same duration, immediately prior) and calculates `((current - previous) / previous) * 100` percentage change

### Frontend Architecture

- **Components** (`frontend/src/components/features/footprint/`) — `PeriodSelector`, `SummaryCard`, `CategoryBreakdownChart`, `TrendChart`, all wrapped with `React.memo`
- **Hooks** (`frontend/src/hooks/useFootprint.ts`) — React Query hooks with 2-minute stale time and 10-minute garbage collection
- **Auto-refresh** — Footprint queries are automatically invalidated when a new activity is logged via `useCreateActivity`

## API Documentation

- OpenAPI spec: `/docs/api-contracts/openapi.yaml`
- Interactive docs: `http://localhost:8000/docs` (when running)

## MCP Integration

The project includes an MCP server for AI agent integration:

```bash
# Start MCP server
docker compose --profile mcp up mcp
```

Available tools:
- `log_activity` - Log a carbon-emitting activity
- `get_footprint_summary` - Get footprint summary for a period
- `compare_to_region` - Compare footprint to regional average

## Environment Variables

See `.env.example` files in `backend/` and `frontend/` directories.

## Contributing

1. Check feature specs in `.agent/specs/features/`
2. Follow conventions in `/.agent/STYLE_GUIDE.md`
3. Create feature branch from `develop`
4. Submit PR with passing CI

## License

MIT
