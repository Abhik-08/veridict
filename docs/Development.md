# Veridict Development & Contribution Guide

This guide covers local environment setup, database migrations, running unit tests, project organization, and code formatting standards for developers.

---

## Workspace Structure Overview

```
veridict/
├── backend/            # FastAPI backend application
│   ├── alembic/        # Database migration scripts (001_initial_schema, 002_history_foundation)
│   ├── app/            # Source code (agents, api, auth, common, core, database, history, knowledge, schemas, services)
│   ├── scripts/dev/    # Developer utility & manual E2E test scripts
│   └── tests/          # Pytest backend test suite (151 unit/integration tests)
├── frontend/           # Vite + React 19 + TypeScript frontend
│   └── src/            # Components, context, hooks, layouts, pages, services, types, utils
├── docs/               # Technical documentation
└── LICENSE             # MIT License
```

---

## Development Setup

### Backend Setup
1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `backend/.env` (see `backend/.env.example`).
4. Apply database migrations:
   ```bash
   alembic stamp 001_initial_schema
   alembic upgrade head
   ```
5. Start backend in hot-reload mode:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Install node dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start dev server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running Tests & Verifications

### Backend Pytest Suite
Run full test suite from `backend/` directory (151 tests, 100% pass rate):
```bash
python -m pytest tests/ -v
```

### Developer Scripts (`scripts/dev/`)
Standalone test scripts are available for debugging individual judge models:
```bash
python scripts/dev/manual_test_accuracy_judge.py
python scripts/dev/manual_test_relevance_judge.py
python scripts/dev/manual_test_hallucination_judge.py
python scripts/dev/e2e_api_test.py
```

### Frontend Build & Type Checks
```bash
cd frontend
npm run build
```
