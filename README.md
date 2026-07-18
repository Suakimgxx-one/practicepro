# PracticePro

AI-powered instrument practice assistant that compares a student's recording
against a professional reference performance and generates grounded,
specific practice feedback (pitch, rhythm, tempo, dynamics).

## Architecture

- `frontend/` — React + TypeScript + Tailwind (Vite)
- `backend/app/` — FastAPI application (routes, DB models, services)
- `backend/analysis_engine/` — standalone, framework-free DSP/ML package
- `backend/worker/` — Celery worker for long-running audio jobs
  (YouTube download via yt-dlp, feature extraction, alignment)
- PostgreSQL — users, recordings, analysis_sessions, analysis_results, feedback
- Redis — Celery broker/result backend

## Local development

```bash
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
```

- API: http://localhost:8000/health, docs at http://localhost:8000/docs
- Frontend: http://localhost:5173
- Postgres: localhost:5433 (mapped from container's 5432 to avoid conflicts
  with a local Postgres install; practicepro/practicepro)

## Running tests

```bash
docker compose exec api pytest -v
```

## Milestones

1. ✅ Scaffolding + Docker Compose + Postgres schema
2. ✅ FastAPI backend skeleton — users/recordings CRUD, schemas, service layer
3. ✅ Audio upload — validation, storage, decodability checks
4. ✅ YouTube ingestion — Celery task, yt-dlp download, auto-enqueue on creation
5. Analysis engine core + DTW alignment
6. Pitch analysis
7. Rhythm analysis
8. Tempo analysis
9. Dynamics analysis
10. Feedback engine (LLM)
11. Frontend — core flow
12. Frontend — visualization
13. Integration + deployment
