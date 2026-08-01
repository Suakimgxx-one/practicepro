import numpy as np
import pytest

from analysis_engine.alignment import align
from analysis_engine.dynamics import compare_dynamics, extract_loudness_contour

SR = 22050
NOTE_FREQS = [261.63, 329.63, 392.00, 523.25]


def _tone(freq: float, duration: float, amplitude: float = 0.3, sr: int = SR) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    waveform = amplitude * np.sin(2 * np.pi * freq * t)
    fade_samples = int(sr * 0.01)
    if fade_samples > 0 and len(waveform) > 2 * fade_samples:
        envelope = np.ones_like(waveform)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        waveform = waveform * envelope
    return waveform


def _make_sequence(
    note_durations: list[float],
    amplitudes: list[float] | None = None,
    freqs: list[float] = NOTE_FREQS,
    sr: int = SR,
) -> np.ndarray:
    amplitudes = amplitudes or [0.3] * len(note_durations)
    return np.concatenate(
        [_tone(f, d, a, sr) for f, d, a in zip(freqs, note_durations, amplitudes)]
    )


def test_compare_dynamics_identical_signals_near_zero_difference():
    waveform = _make_sequence([0.8, 0.8, 0.8, 0.8])
    reference_contour = extract_loudness_contour(waveform, SR)
    student_contour = extract_loudness_contour(waveform, SR)
    alignment = align(waveform, SR, waveform, SR)
    result = compare_dynamics(reference_contour, student_contour, alignment)
    assert len(result.points) > 0
    assert result.mean_absolute_loudness_difference < 1.0


def test_compare_dynamics_detects_uniformly_quieter_performance():
    reference = _make_sequence([0.8, 0.8, 0.8, 0.8], amplitudes=[0.3, 0.3, 0.3, 0.3])
    student = _make_sequence([0.8, 0.8, 0.8, 0.8], amplitudes=[0.15, 0.15, 0.15, 0.15])
    reference_contour = extract_loudness_contour(reference, SR)
    student_contour = extract_loudness_contour(student, SR)
    alignment = align(reference, SR, student, SR)
    result = compare_dynamics(reference_contour, student_contour, alignment)
    assert len(result.points) > 0
    mean_diff = np.mean([p.loudness_difference_db for p in result.points])
    assert mean_diff == pytest.approx(-6.0, abs=2.0)


def test_compare_dynamics_flags_a_louder_passage():
    reference = _make_sequence([0.8, 0.8], amplitudes=[0.2, 0.2], freqs=[261.63, 329.63])
    student = _make_sequence([0.8, 0.8], amplitudes=[0.2, 0.6], freqs=[261.63, 329.63])
    reference_contour = extract_loudness_contour(reference, SR)
    student_contour = extract_loudness_contour(student, SR)
    alignment = align(reference, SR, student, SR)
    result = compare_dynamics(reference_contour, student_contour, alignment)
    regions = result.flagged_regions(threshold_db=4.0)
    louder_regions = [r for r in regions if r[2] == "louder_than_reference"]
    assert len(louder_regions) >= 1
    start, end, _label = louder_regions[0]
    assert start >= 0.5
