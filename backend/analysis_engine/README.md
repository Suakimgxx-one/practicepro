# analysis_engine

Standalone, framework-free Python package. No FastAPI, Celery, or DB imports
belong in here — everything in this package should be importable and unit
testable with plain numpy arrays as input, independent of the web app.

Modules land here starting Milestone 5:
- `alignment.py` — DTW-based alignment between reference and student audio
- `pitch.py` — F0 extraction (CREPE) + pitch comparison
- `rhythm.py` — onset detection + timing comparison
- `tempo.py` — beat tracking + tempo curve comparison
- `dynamics.py` — loudness contour (pyloudnorm) + comparison
- `feedback_llm.py` — structured analysis JSON -> natural language feedback
