# analysis_engine

Standalone, framework-free Python package. No FastAPI, Celery, or DB imports
belong in here — everything in this package should be importable and unit
testable with plain numpy arrays as input, independent of the web app.

Modules:
- `alignment.py` — DTW-based alignment between reference and student audio (Milestone 5)
- `pitch.py` — F0 extraction (pYIN) + pitch comparison in cents (Milestone 6)
- `rhythm.py` — onset detection + timing comparison (Milestone 7)
- `tempo.py` — local tempo ratio from the alignment path + beat-tracked BPM (Milestone 8)
- `dynamics.py` — LUFS loudness contour + comparison (Milestone 9)
- `feedback_llm.py` — structured analysis JSON -> natural language feedback (Milestone 10, upcoming)
