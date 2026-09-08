import json
from typing import Any

from analysis_engine.dynamics import DynamicsComparisonResult
from analysis_engine.pitch import PitchComparisonResult
from analysis_engine.rhythm import RhythmComparisonResult
from analysis_engine.tempo import TempoComparisonResult


def build_analysis_summary(pitch=None, rhythm=None, tempo=None, dynamics=None):
    summary = {}
    if pitch is not None:
        summary["pitch"] = {
            "mean_absolute_cents_deviation": round(pitch.mean_absolute_cents_deviation, 1),
            "flagged_regions": [{"start": round(s, 2), "end": round(e, 2), "issue": "out_of_tune"} for s, e in pitch.flagged_regions()],
        }
    if rhythm is not None:
        summary["rhythm"] = {
            "mean_absolute_timing_offset_seconds": round(rhythm.mean_absolute_timing_offset, 3),
            "unmatched_reference_onsets": rhythm.unmatched_reference_onsets,
            "unmatched_student_onsets": rhythm.unmatched_student_onsets,
            "flagged_regions": [{"start": round(s, 2), "end": round(e, 2), "issue": "timing_off"} for s, e in rhythm.flagged_regions()],
        }
    if tempo is not None:
        summary["tempo"] = {
            "mean_tempo_ratio": round(tempo.mean_tempo_ratio, 3),
            "reference_average_bpm": round(tempo.reference_average_bpm, 1) if tempo.reference_average_bpm else None,
            "student_average_bpm": round(tempo.student_average_bpm, 1) if tempo.student_average_bpm else None,
            "flagged_regions": [{"start": round(s, 2), "end": round(e, 2), "issue": label} for s, e, label in tempo.flagged_regions()],
        }
    if dynamics is not None:
        summary["dynamics"] = {
            "mean_absolute_loudness_difference_db": round(dynamics.mean_absolute_loudness_difference, 1),
            "flagged_regions": [{"start": round(s, 2), "end": round(e, 2), "issue": label} for s, e, label in dynamics.flagged_regions()],
        }
    return summary


FEEDBACK_SYSTEM_PROMPT = """You are a precise, technically-minded music practice coach. You will be given structured measurement data comparing a student's instrumental performance against a professional reference recording of the same piece. The data includes flagged time regions and summary statistics for pitch, rhythm, tempo, and dynamics.

Generate specific, actionable feedback messages based ONLY on the data provided. Every message must reference a specific measurement or time region from the data — never invent details, timestamps, or issues that aren't present in the input.

Tone: direct and technical. Do not soften findings with excessive praise or hedging. State what the measurement shows and what it means musically, the way a conservatory-level instructor would in a lesson. Do not use generic advice like "practice more" or "work on your technique" — every message must be grounded in what the data actually shows.

Detail level: generate one feedback message per flagged region in the input (not a compressed summary). If a category has flagged regions, cover each one individually. Only generate an overall summary message for a category if it has no flagged regions but a notably high or low headline stat worth naming; skip categories entirely if there's nothing meaningful to report.

Respond with ONLY a JSON array, no other text, no markdown code fences. Each element must be an object with exactly these keys:
- "category": one of "pitch", "rhythm", "tempo", "dynamics"
- "text": the feedback message (one to two sentences, direct and specific)
- "timestamp_reference": a number (seconds) pointing to the relevant moment, or null if the message applies to the whole piece

Example message style: "Pitch drifts sharp by roughly 30 cents from 0:42 to 0:47 — check the embouchure on the sustained high passage there." Not: "Try to work on your intonation in this section!\""""


def generate_feedback(summary, client, model="claude-sonnet-4-6"):
    if not summary:
        return []
    response = client.messages.create(
        model=model, max_tokens=1536, system=FEEDBACK_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(summary)}],
    )
    raw_text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Feedback model did not return valid JSON: {raw_text[:200]}") from e
    if not isinstance(parsed, list):
        raise ValueError(f"Expected a JSON array of feedback items, got: {type(parsed)}")
    valid_categories = {"pitch", "rhythm", "tempo", "dynamics"}
    feedback_items = []
    for item in parsed:
        if not isinstance(item, dict) or "category" not in item or "text" not in item:
            continue
        if item["category"] not in valid_categories:
            continue
        feedback_items.append({"category": item["category"], "text": str(item["text"]), "timestamp_reference": item.get("timestamp_reference")})
    return feedback_items
