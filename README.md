# PracticePro

A practice journal for musicians: organize your work by piece, compare each
practice attempt against a professional reference performance, and track
your progress over time — pitch, rhythm, tempo, and dynamics, plus
LLM-generated coaching notes grounded in the actual measurements.

## Architecture

- `frontend/` — React + TypeScript + Tailwind (Vite), React Router
- `backend/app/` — FastAPI application (routes, DB models, services)
- `backend/analysis_engine/` — standalone, framework-free DSP/ML package
  (DTW alignment, pitch/rhythm/tempo/dynamics comparison, LLM feedback)
- `backend/worker/` — Celery worker: YouTube ingestion + full analysis
  pipeline orchestration
- PostgreSQL — users, pieces, recordings, analysis_sessions,
  analysis_results, feedback
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

## Core flow

1. Add a piece you're practicing (just a title)
2. Attach a reference performance (YouTube link) — the piece's one
   professional recording to compare against
3. Log a practice attempt (upload audio) — as many times as you like
4. Each attempt can be compared against the reference: alignment,
   pitch/rhythm/tempo/dynamics analysis, and LLM feedback, all persisted
5. The piece's progress view charts pitch accuracy across every
   completed attempt, so improvement (or regression) over time is visible

## Milestones

1-10. ✅ Backend: scaffolding through the LLM feedback engine
11. ✅ Frontend — core flow
12. ✅ Frontend — visualization (charts + feedback display)
     + Pieces feature (organize practice by piece, track progress over time)
     + visual redesign
13. Deployment
