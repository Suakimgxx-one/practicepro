import numpy as np
import pytest

from analysis_engine.alignment import align

SR = 22050

# A simple 4-note arpeggio (C4, E4, G4, C5) — each note is a distinct
# pitch class, so chroma features should discriminate between them
# cleanly, which is what makes the alignment testable/predictable.
NOTE_FREQS = [261.63, 329.63, 392.00, 523.25]


def _tone(freq: float, duration: float, sr: int = SR) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    waveform = 0.3 * np.sin(2 * np.pi * freq * t)

    # Short fade in/out avoids clicks at note boundaries, which would
    # otherwise inject spurious broadband noise into the chroma
    # features right at the transitions we care about most.
    fade_samples = int(sr * 0.01)
    if fade_samples > 0 and len(waveform) > 2 * fade_samples:
        envelope = np.ones_like(waveform)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        waveform = waveform * envelope

    return waveform


def _make_sequence(note_durations: list[float], sr: int = SR) -> np.ndarray:
    return np.concatenate(
        [_tone(freq, dur, sr) for freq, dur in zip(NOTE_FREQS, note_durations)]
    )


def test_align_identical_signals_maps_time_to_itself():
    """Aligning a recording to itself should be close to the identity
    mapping — the simplest possible sanity check on the whole pipeline."""
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    result = align(waveform, SR, waveform, SR)

    for t in [0.1, 0.6, 1.1, 1.9]:
        assert result.reference_to_student(t) == pytest.approx(t, abs=0.15)


def test_align_detects_dragged_passage():
    """
    The student holds the second note twice as long as the reference.
    A point early in note 1 (untouched) should map close to itself; a
    point after the drag should map to a correspondingly later point
    in the student's timeline, roughly by the amount of extra time
    inserted.
    """
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])  # total 2.0s
    student = _make_sequence([0.5, 1.0, 0.5, 0.5])  # total 2.5s — note 2 dragged

    result = align(reference, SR, student, SR)

    assert result.reference_to_student(0.2) == pytest.approx(0.2, abs=0.15)

    # Reference time 1.75s falls in note 4; by then, 0.5s of drag has
    # already been inserted in the student's timeline, so it should
    # map to roughly 2.25s, not 1.75s.
    mapped = result.reference_to_student(1.75)
    assert mapped > 1.75
    assert mapped == pytest.approx(2.25, abs=0.2)


def test_align_returns_chronologically_ordered_times():
    """The warping path must move forward in time on both sides —
    DTW's monotonicity constraint means neither timeline can run
    backwards, even though multiple frames can map to the same instant
    (a held or rushed note)."""
    reference = _make_sequence([0.4, 0.6, 0.4, 0.6])
    student = _make_sequence([0.6, 0.4, 0.6, 0.4])

    result = align(reference, SR, student, SR)

    assert np.all(np.diff(result.reference_times) >= 0)
    assert np.all(np.diff(result.student_times) >= -1e-6)


def test_align_cost_is_lower_for_more_similar_performances():
    """A student performance that's just tempo-shifted should score a
    lower (better) alignment cost than one that's playing entirely
    different notes."""
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    similar_student = _make_sequence([0.4, 0.6, 0.5, 0.5])  # same notes, slightly different timing

    # Different notes entirely (reversed note order) — a genuinely
    # different performance, not just a timing variation.
    different_student = np.concatenate(
        [_tone(freq, 0.5, SR) for freq in list(reversed(NOTE_FREQS))]
    )

    similar_result = align(reference, SR, similar_student, SR)
    different_result = align(reference, SR, different_student, SR)

    assert similar_result.cost < different_result.cost
