import anthropic

from analysis_engine.dynamics import DynamicsComparisonResult
from analysis_engine.feedback import build_analysis_summary, generate_feedback
from analysis_engine.pitch import PitchComparisonResult
from analysis_engine.rhythm import RhythmComparisonResult
from analysis_engine.tempo import TempoComparisonResult
from app.core.config import settings


def generate_feedback_for_session(
    pitch: PitchComparisonResult | None = None,
    rhythm: RhythmComparisonResult | None = None,
    tempo: TempoComparisonResult | None = None,
    dynamics: DynamicsComparisonResult | None = None,
) -> list[dict]:
    summary = build_analysis_summary(pitch, rhythm, tempo, dynamics)
    if not summary:
        return []

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return generate_feedback(summary, client, model=settings.FEEDBACK_MODEL)
