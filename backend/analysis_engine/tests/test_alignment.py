import numpy as np
import pytest
from analysis_engine.alignment import align

SR = 22050
NOTE_FREQS = [261.63, 329.63, 392.00, 523.25]


def _tone(freq, duration, sr=SR):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    waveform = 0.3 * np.sin(2 * np.pi * freq * t)
    fade_samples = int(sr * 0.01)
    if fade_samples > 0 and len(waveform) > 2 * fade_samples:
        envelope = np.ones_like(waveform)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        waveform = waveform * envelope
    return waveform


def _make_sequence(note_durations, sr=SR):
    return np.concatenate([_tone(freq, dur, sr) for freq, dur in zip(NOTE_FREQS, note_durations)])


def test_align_identical_signals_maps_time_to_itself():
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    result = align(waveform, SR, waveform, SR)
    for t in [0.1, 0.6, 1.1, 1.9]:
        assert result.reference_to_student(t) == pytest.approx(t, abs=0.15)


def test_align_detects_dragged_passage():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    student = _make_sequence([0.5, 1.0, 0.5, 0.5])
    result = align(reference, SR, student, SR)
    assert result.reference_to_student(0.2) == pytest.approx(0.2, abs=0.15)
    mapped = result.reference_to_student(1.75)
    assert mapped > 1.75
    assert mapped == pytest.approx(2.25, abs=0.2)


def test_align_returns_chronologically_ordered_times():
    reference = _make_sequence([0.4, 0.6, 0.4, 0.6])
    student = _make_sequence([0.6, 0.4, 0.6, 0.4])
    result = align(reference, SR, student, SR)
    assert np.all(np.diff(result.reference_times) >= 0)
    assert np.all(np.diff(result.student_times) >= -1e-6)


def test_align_cost_is_lower_for_more_similar_performances():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    similar_student = _make_sequence([0.4, 0.6, 0.5, 0.5])
    different_student = np.concatenate([_tone(freq, 0.5, SR) for freq in list(reversed(NOTE_FREQS))])
    similar_result = align(reference, SR, similar_student, SR)
    different_result = align(reference, SR, different_student, SR)
    assert similar_result.cost < different_result.cost
