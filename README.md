# PracticePro

AI-powered instrument practice assistant that compares a student's recording
against a professional reference performance and generates grounded,
specific practice feedback (pitch, rhythm, tempo, dynamics).

## Architecture

- `frontend/` — React + TypeScript + Tailwind (Vite)
- `backend/app/` — FastAPI application (routes, DB models, services)
- `backend/analysis_engine/` — standalone, framework-free DSP/ML package
  (DTW alignment, pitch/rhythm/tempo/dynamics comparison)
- `backend/worker/` — Celery worker for long-running audio jobs
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
- Postgres: localhost:5433 (mapped from container's 5432)

## Running tests

```bash
docker compose exec api pytest -v
```

## Milestones

1. ✅ Scaffolding + Docker Compose + Postgres schema
2. ✅ FastAPI backend skeleton
3. ✅ Audio upload — validation, storage, decodability checks
4. ✅ YouTube ingestion — Celery task, yt-dlp download
5. ✅ Analysis engine core + DTW alignment (chroma features)
6. ✅ Pitch analysis — pYIN extraction + cents deviation comparison
7. ✅ Rhythm analysis — onset detection + timing comparison
8. ✅ Tempo analysis — alignment-path tempo ratio + best-effort BPM
9. ✅ Dynamics analysis — LUFS loudness comparison
10. ✅ Feedback engine — LLM-generated coaching text, grounded in measured data
11. Frontend — core flow
12. Frontend — visualization
13. Integration + deployment
