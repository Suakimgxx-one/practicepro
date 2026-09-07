import logging

import anthropic

from analysis_engine.alignment import align
from analysis_engine.dynamics import compare_dynamics, extract_loudness_contour
from analysis_engine.features import load_audio
from analysis_engine.feedback import build_analysis_summary, generate_feedback
from analysis_engine.pitch import compare_pitch, extract_pitch_contour
from analysis_engine.rhythm import compare_rhythm, detect_onsets
from analysis_engine.tempo import compare_tempo
from app.core.config import settings
from app.db.session import SyncSessionLocal
from app.models.analysis import AnalysisCategory, AnalysisResult, AnalysisSession, SessionStatus
from app.models.feedback import Feedback
from app.models.recording import Recording
from worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="analyze.process_analysis_session", bind=True, max_retries=1)
def process_analysis_session(self, session_id: str) -> None:
    """
    Runs the full pipeline for an analysis session: load both
    recordings' audio -> DTW alignment -> pitch/rhythm/tempo/dynamics
    comparison -> persist structured results -> LLM feedback
    generation (best-effort) -> mark complete.

    Uses a plain sync DB session, same reasoning as the YouTube
    ingestion task in worker/tasks/ingest.py — Celery's default worker
    model runs tasks outside any asyncio event loop.
    """
    session = SyncSessionLocal()
    try:
        analysis_session = session.get(AnalysisSession, session_id)
        if analysis_session is None:
            logger.error("AnalysisSession %s not found, aborting", session_id)
            return

        reference = session.get(Recording, analysis_session.reference_recording_id)
        student = session.get(Recording, analysis_session.student_recording_id)

        if (
            reference is None
            or student is None
            or not reference.storage_path
            or not student.storage_path
        ):
            logger.error(
                "AnalysisSession %s references recordings that aren't ready", session_id
            )
            analysis_session.status = SessionStatus.FAILED
            session.commit()
            return

        analysis_session.status = SessionStatus.ALIGNING
        session.commit()

        try:
            reference_waveform, reference_sr = load_audio(reference.storage_path)
            student_waveform, student_sr = load_audio(student.storage_path)
            alignment = align(reference_waveform, reference_sr, student_waveform, student_sr)

            analysis_session.status = SessionStatus.ANALYZING
            session.commit()

            reference_pitch = extract_pitch_contour(reference_waveform, reference_sr)
            student_pitch = extract_pitch_contour(student_waveform, student_sr)
            pitch_result = compare_pitch(reference_pitch, student_pitch, alignment)

            reference_onsets = detect_onsets(reference_waveform, reference_sr)
            student_onsets = detect_onsets(student_waveform, student_sr)
            rhythm_result = compare_rhythm(reference_onsets, student_onsets, alignment)

            tempo_result = compare_tempo(
                reference_waveform, reference_sr, student_waveform, student_sr, alignment
            )

            reference_loudness = extract_loudness_contour(reference_waveform, reference_sr)
            student_loudness = extract_loudness_contour(student_waveform, student_sr)
            dynamics_result = compare_dynamics(reference_loudness, student_loudness, alignment)
        except Exception:
            logger.exception("Analysis pipeline failed for session %s", session_id)
            analysis_session.status = SessionStatus.FAILED
            session.commit()
            return

        # Persist structured results per category. Includes both
        # summary stats and enough per-point data for the frontend to
        # render actual curves (Milestone 12), not just headline numbers.
        results_payload = {
            AnalysisCategory.PITCH: {
                "mean_absolute_cents_deviation": round(pitch_result.mean_absolute_cents_deviation, 1),
                "flagged_regions": [
                    {"start": s, "end": e} for s, e in pitch_result.flagged_regions()
                ],
                "points": [
                    {
                        "reference_time": round(p.reference_time, 3),
                        "cents_deviation": round(p.cents_deviation, 1),
                    }
                    for p in pitch_result.points
                ],
            },
            AnalysisCategory.RHYTHM: {
                "mean_absolute_timing_offset_seconds": round(
                    rhythm_result.mean_absolute_timing_offset, 3
                ),
                "unmatched_reference_onsets": rhythm_result.unmatched_reference_onsets,
                "unmatched_student_onsets": rhythm_result.unmatched_student_onsets,
                "flagged_regions": [
                    {"start": s, "end": e} for s, e in rhythm_result.flagged_regions()
                ],
            },
            AnalysisCategory.TEMPO: {
                "mean_tempo_ratio": round(tempo_result.mean_tempo_ratio, 3),
                "reference_average_bpm": tempo_result.reference_average_bpm,
                "student_average_bpm": tempo_result.student_average_bpm,
                "flagged_regions": [
                    {"start": s, "end": e, "label": label}
                    for s, e, label in tempo_result.flagged_regions()
                ],
                "points": [
                    {
                        "reference_time": round(p.reference_time, 3),
                        "local_tempo_ratio": round(p.local_tempo_ratio, 3),
                    }
                    for p in tempo_result.points
                ],
            },
            AnalysisCategory.DYNAMICS: {
                "mean_absolute_loudness_difference_db": round(
                    dynamics_result.mean_absolute_loudness_difference, 1
                ),
                "flagged_regions": [
                    {"start": s, "end": e, "label": label}
                    for s, e, label in dynamics_result.flagged_regions()
                ],
            },
        }

        for category, data in results_payload.items():
            session.add(AnalysisResult(session_id=analysis_session.id, category=category, data=data))
        session.commit()

        # Feedback generation is best-effort: a failure here (e.g. no
        # API key configured, or a transient API error) shouldn't sink
        # an otherwise-successful analysis. The measured results above
        # are already saved regardless of what happens here.
        try:
            summary = build_analysis_summary(
                pitch_result, rhythm_result, tempo_result, dynamics_result
            )
            if summary and settings.ANTHROPIC_API_KEY:
                client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                feedback_items = generate_feedback(summary, client, model=settings.FEEDBACK_MODEL)
                for item in feedback_items:
                    session.add(
                        Feedback(
                            session_id=analysis_session.id,
                            category=AnalysisCategory(item["category"]),
                            text=item["text"],
                            timestamp_reference=item.get("timestamp_reference"),
                        )
                    )
                session.commit()
        except Exception:
            logger.exception(
                "Feedback generation failed for session %s (non-fatal, results still saved)",
                session_id,
            )

        analysis_session.status = SessionStatus.COMPLETE
        session.commit()
    finally:
        session.close()
