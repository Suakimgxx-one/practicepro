# PracticePro

AI-powered instrument practice assistant that compares a student's recording
against a professional reference performance and generates grounded,
specific practice feedback (pitch, rhythm, tempo, dynamics).

## Architecture

- `frontend/` — React + TypeScript + Tailwind (Vite)
- `backend/app/` — FastAPI application (routes, DB models, services)
- `backend/analysis_engine/` — standalone, framework-free DSP/ML package
  (DTW alignment, pitch/rhythm/tempo/dynamics comparison, LLM feedback)
- `backend/worker/` — Celery worker: YouTube ingestion + full analysis
  pipeline orchestration (`worker/tasks/analyze.py`)
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

To generate real LLM feedback (optional — everything else works without
it), add a real key to `ANTHROPIC_API_KEY` in `.env`.

## Running tests

```bash
docker compose exec api pytest -v
```

## Core flow

1. `POST /api/v1/recordings` (source=upload or youtube) — register a recording
2. Upload audio or wait for YouTube ingestion to complete (poll `GET /recordings/{id}`)
3. Once both a reference and student recording are `status: ready`:
   `POST /api/v1/analysis-sessions` with both recording IDs
4. Poll `GET /api/v1/analysis-sessions/{id}` until `status: complete` —
   returns full pitch/rhythm/tempo/dynamics results plus LLM feedback

## Milestones

1. ✅ Scaffolding + Docker Compose + Postgres schema
2. ✅ FastAPI backend skeleton
3. ✅ Audio upload — validation, storage, decodability checks
4. ✅ YouTube ingestion — Celery task, yt-dlp download
5. ✅ Analysis engine core + DTW alignment
6. ✅ Pitch analysis — pYIN + cents deviation comparison
7. ✅ Rhythm analysis — onset detection + timing comparison
8. ✅ Tempo analysis — alignment-path tempo ratio + best-effort BPM
9. ✅ Dynamics analysis — LUFS loudness comparison
10. ✅ Feedback engine — LLM-generated coaching text
11. ✅ Frontend — core flow (user session, YouTube + upload inputs, status polling)
    + analysis-session orchestration endpoint (pulled forward from Milestone 13)
12. Frontend — visualization (charts + feedback display for analysis results)
13. Integration + deployment
