# Development Setup Guide

This guide covers local development setup for the Carbon Footprint Tracker.

## Prerequisites

### Required Software
- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 15+** - Database (local or Supabase)
- **Git** - Version control
- **Docker** (optional) - For containerized development

### Recommended Tools
- **VS Code** or **Cursor** with extensions:
  - Python (ms-python.python)
  - Pylance (ms-python.vscode-pylance)
  - ESLint (dbaeumer.vscode-eslint)
  - Tailwind CSS IntelliSense
- **Postman** or **Bruno** - API testing
- **TablePlus** or **pgAdmin** - Database GUI

## Backend Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd carbon-tracker
```

### 2. Create Virtual Environment
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
# Required:
# - SUPABASE_URL: Your Supabase project URL
# - SUPABASE_ANON_KEY: Supabase anonymous key
# - SUPABASE_JWT_SECRET: JWT signing secret from Supabase
```

### 5. Database Setup

#### Option A: Supabase (Recommended)
1. Create project at [supabase.com](https://supabase.com)
2. Get project URL and anon key from project settings
3. Update `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
4. Apply schema via Supabase dashboard SQL editor or Supabase CLI

#### Option B: Local PostgreSQL (for offline development)
```bash
# Create database
createdb carbon_tracker
```

### 6. Seed Data (Optional)
```bash
# Run seed script to populate emission factors
python -m src.infrastructure.scripts.seed_emission_factors
```

### 7. Run Backend
```bash
# Development mode (auto-reload)
uvicorn src.api.main:app --reload --port 8000

# With environment variable
ENVIRONMENT=development uvicorn src.api.main:app --reload
```

Backend should now be running at `http://localhost:8000`

API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

### 1. Navigate to Frontend
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 4. Run Frontend
```bash
npm run dev
```

Frontend should now be running at `http://localhost:5173`

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### Frontend Access
Open browser to `http://localhost:5173`
- Should see landing page
- No console errors

### Database Connection
```bash
# In backend directory
python -c "from src.infrastructure.config.supabase import get_client; print('Connected!')"
```

## Common Commands

### Backend
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Lint
ruff check . --fix

# Type check
mypy src

# Format
ruff format .

# Migrations managed via Supabase dashboard/SQL editor
# Use Supabase CLI for local migration workflows if needed
```

### Frontend
```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Fix lint issues
npm run lint:fix

# Type check
npm run typecheck

# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker Setup (Alternative)

### Using Docker Compose
```bash
# From project root
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

## Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:** Activate virtual environment and reinstall dependencies
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Issue:** `Supabase connection error` or `Invalid API key`
**Solution:** Verify your Supabase credentials in `.env`
```bash
# Ensure SUPABASE_URL and SUPABASE_ANON_KEY are correct
# Check project settings at https://supabase.com/dashboard
```

**Issue:** `CORS error` when calling API from frontend
**Solution:** Add frontend URL to CORS_ORIGINS in backend .env
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Won't Start

**Issue:** `Cannot find module 'react'`
**Solution:** Install dependencies
```bash
npm install
```

**Issue:** `VITE_API_BASE_URL is undefined`
**Solution:** Create .env file in frontend directory
```bash
cp .env.example .env
# Edit .env with correct values
```

**Issue:** API calls return 404
**Solution:** Verify backend is running and VITE_API_BASE_URL is correct
```bash
# Check backend health
curl http://localhost:8000/health

# Verify .env has correct URL
cat .env | grep VITE_API_BASE_URL
```

### Database Issues

**Issue:** `psycopg2.OperationalError: could not connect to server`
**Solution:** Ensure PostgreSQL is running
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (Mac with Homebrew)
brew services start postgresql

# Start PostgreSQL (Linux)
sudo systemctl start postgresql
```

**Issue:** Missing tables or schema mismatch
**Solution:** Apply schema via Supabase dashboard SQL editor or Supabase CLI
```bash
# Schema is managed via Supabase
# Check the Supabase dashboard Table Editor for current schema
```

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| SUPABASE_SERVICE_ROLE_KEY | No | Supabase service role key (server-side only) | `eyJhbGc...` |
| SUPABASE_URL | Yes | Supabase project URL | `https://xxx.supabase.co` |
| SUPABASE_ANON_KEY | Yes | Supabase anonymous key | `eyJhbGc...` |
| SUPABASE_JWT_SECRET | Yes | JWT signing secret | `your-jwt-secret` |
| ENVIRONMENT | No | Environment name | `development` (default) |
| LOG_LEVEL | No | Logging level | `DEBUG`, `INFO`, `WARNING` |
| CORS_ORIGINS | No | Allowed CORS origins | `http://localhost:5173` |
| IP_API_KEY | No | IP geolocation API key | For region detection |

### Frontend (.env)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| VITE_API_BASE_URL | Yes | Backend API URL | `http://localhost:8000/api/v1` |
| VITE_SUPABASE_URL | Yes | Supabase project URL | `https://xxx.supabase.co` |
| VITE_SUPABASE_ANON_KEY | Yes | Supabase anonymous key | `eyJhbGc...` |

## Development Workflow

### Starting Work
```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/activity-logging

# 3. Start backend (terminal 1)
cd backend
source venv/bin/activate
uvicorn src.api.main:app --reload

# 4. Start frontend (terminal 2)
cd frontend
npm run dev

# 5. Start coding!
```

### Before Committing
```bash
# Backend checks
cd backend
pytest
ruff check . --fix
mypy src

# Frontend checks
cd frontend
npm run typecheck
npm run lint:fix
npm test
```

### Committing Changes
```bash
git add .
git commit -m "feat(activity): add transport logging form"
git push origin feature/activity-logging
```

## IDE Configuration

### VS Code (settings.json)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    }
  },
  "[typescriptreact]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    }
  },
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*)[\"'`]"]
  ]
}
```

### Recommended VS Code Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- ESLint (dbaeumer.vscode-eslint)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
- Error Lens (usernamehw.errorlens)
- GitLens (eamodio.gitlens)

## Next Steps

1. Read [ARCHITECTURE.md](.agent/ARCHITECTURE.md) to understand system design
2. Review [STYLE_GUIDE.md](.agent/STYLE_GUIDE.md) for coding conventions
3. Check [TESTING_GUIDE.md](.agent/TESTING_GUIDE.md) for testing patterns
4. Browse feature specs in `.agent/specs/features/`
5. Start with a small feature to familiarize yourself with the codebase

## Getting Help

- Check [README.md](.agent/README.md) for agent system overview
- Review [ARCHITECTURE.md](.agent/ARCHITECTURE.md) for design decisions
- Look at existing code for patterns
- Check ADRs in `docs/adr/` for architecture decisions
