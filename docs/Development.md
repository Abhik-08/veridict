# Veridict Development & Contribution Guide

This guide covers local environment setup, running unit tests, project organization, and code formatting standards for developers.

---

## Workspace Structure Overview

```
veridict/
├── backend/            # FastAPI backend application
│   ├── app/            # Source code (agents, api, core, knowledge, schemas, services)
│   ├── scripts/dev/    # Developer utility & manual E2E test scripts
│   └── tests/          # Pytest backend test suite (123 unit/integration tests)
├── frontend/           # Vite + React 19 + TypeScript frontend
│   └── src/            # Components, hooks, layouts, pages, services, types
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
4. Start backend in hot-reload mode:
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

---

## Running Tests

### Backend Pytest Suite
Run full test suite from `backend/` directory:
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

### Frontend Linting & Type Checks
```bash
cd frontend
npm run lint
npm run build
```
