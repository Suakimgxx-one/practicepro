import numpy as np
import pytest
from analysis_engine.alignment import align
from analysis_engine.tempo import compare_tempo, compute_tempo_ratio_curve, estimate_average_bpm

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

def _make_sequence(note_durations, freqs=NOTE_FREQS, sr=SR):
    return np.concatenate([_tone(f, d, sr) for f, d in zip(freqs, note_durations)])

def test_tempo_ratio_curve_near_one_for_identical_signals():
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    alignment = align(waveform, SR, waveform, SR)
    points = compute_tempo_ratio_curve(alignment, sample_interval=0.2)
    assert len(points) > 0
    assert np.mean([p.local_tempo_ratio for p in points]) == pytest.approx(1.0, abs=0.2)

def test_tempo_ratio_curve_detects_dragging_section():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    student = _make_sequence([0.5, 1.0, 0.5, 0.5])
    alignment = align(reference, SR, student, SR)
    points = compute_tempo_ratio_curve(alignment, sample_interval=0.1)
    assert len(points) > 0
    before_drag = min(points, key=lambda p: abs(p.reference_time - 0.25))
    assert before_drag.local_tempo_ratio == pytest.approx(1.0, abs=0.3)
    during_drag = min(points, key=lambda p: abs(p.reference_time - 0.75))
    assert during_drag.local_tempo_ratio > 1.3

def test_estimate_average_bpm_does_not_crash():
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    bpm = estimate_average_bpm(waveform, SR)
    assert bpm is None or bpm > 0

def test_compare_tempo_flags_dragging_region():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    student = _make_sequence([0.5, 1.0, 0.5, 0.5])
    alignment = align(reference, SR, student, SR)
    result = compare_tempo(reference, SR, student, SR, alignment, sample_interval=0.1)
    regions = result.flagged_regions(ratio_threshold=0.15)
    dragging_regions = [r for r in regions if r[2] == "dragging"]
    assert len(dragging_regions) >= 1
    start, end, label = dragging_regions[0]
    assert start < 1.0
    assert end > 0.5
