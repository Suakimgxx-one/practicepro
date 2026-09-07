# analysis_engine

Standalone, framework-free Python package. No FastAPI, Celery, or DB imports
belong in here — everything in this package should be importable and unit
testable with plain numpy arrays as input, independent of the web app.

Modules:
- `alignment.py` — DTW-based alignment (Milestone 5)
- `pitch.py` — F0 extraction (pYIN) + pitch comparison in cents (Milestone 6)
- `rhythm.py` — onset detection + timing comparison (Milestone 7)
- `tempo.py` — local tempo ratio from the alignment path + BPM (Milestone 8)
- `dynamics.py` — LUFS loudness contour + comparison (Milestone 9)
- `feedback.py` — structured summary -> LLM-generated coaching text (Milestone 10)

Orchestration of the full pipeline (load audio -> align -> compare all
four dimensions -> generate feedback -> persist) lives in
worker/tasks/analyze.py, wired to the API via
app/services/analysis_service.py and the /analysis-sessions endpoints.
