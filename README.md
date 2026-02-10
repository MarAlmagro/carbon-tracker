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
