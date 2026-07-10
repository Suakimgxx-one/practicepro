# PracticePro

AI-powered instrument practice assistant that compares a student's recording
against a professional reference performance and generates grounded,
specific practice feedback (pitch, rhythm, tempo, dynamics).

## Architecture

- `frontend/` — React + TypeScript + Tailwind (Vite)
- `backend/app/` — FastAPI application (routes, DB models, services)
- `backend/analysis_engine/` — standalone, framework-free DSP/ML package
  (DTW alignment, pitch/rhythm/tempo/dynamics analysis, feedback generation).
  Independently unit-testable, imported by both the API and the worker.
- `backend/worker/` — Celery worker for long-running audio jobs
  (YouTube download, feature extraction, alignment)
- PostgreSQL — users, recordings, analysis_sessions, analysis_results, feedback
- Redis — Celery broker/result backend

## Local development

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000/health
- Frontend: http://localhost:5173
- Postgres: localhost:5432 (practicepro/practicepro)

## Running migrations

```bash
docker compose exec api alembic upgrade head
```

## Running tests

```bash
docker compose exec api pytest
```

## Milestones

See project roadmap. Each milestone is independently testable:

1. Scaffolding + Docker Compose + Postgres schema (this milestone)
2. FastAPI backend skeleton
3. Audio upload
4. YouTube ingestion
5. Analysis engine core + DTW alignment
6. Pitch analysis
7. Rhythm analysis
8. Tempo analysis
9. Dynamics analysis
10. Feedback engine (LLM)
11. Frontend — core flow
12. Frontend — visualization
13. Integration + deployment
# practicepro
