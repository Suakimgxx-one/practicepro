import numpy as np
import pytest
from analysis_engine.alignment import align
from analysis_engine.rhythm import compare_rhythm, detect_onsets

SR = 22050
NOTE_FREQS = [261.63, 329.63, 392.00, 523.25]


def _tone(freq, duration, sr=SR):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    waveform = 0.3 * np.sin(2 * np.pi * freq * t)
    fade_samples = int(sr * 0.005)
    if fade_samples > 0 and len(waveform) > 2 * fade_samples:
        envelope = np.ones_like(waveform)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        waveform = waveform * envelope
    return waveform


def _make_sequence(note_durations, freqs=NOTE_FREQS, sr=SR):
    return np.concatenate([_tone(f, d, sr) for f, d in zip(freqs, note_durations)])


def test_detect_onsets_finds_approximately_correct_count():
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    onsets = detect_onsets(waveform, SR)
    assert 3 <= len(onsets) <= 6


def test_compare_rhythm_identical_performance_near_zero_offset():
    waveform = _make_sequence([0.5, 0.5, 0.5, 0.5])
    ref_onsets = detect_onsets(waveform, SR)
    student_onsets = detect_onsets(waveform, SR)
    alignment = align(waveform, SR, waveform, SR)
    result = compare_rhythm(ref_onsets, student_onsets, alignment)
    assert len(result.points) > 0
    assert result.mean_absolute_timing_offset < 0.1


def test_compare_rhythm_absorbs_consistent_tempo_drag():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    student = _make_sequence([0.5, 1.0, 0.5, 0.5])
    ref_onsets = detect_onsets(reference, SR)
    student_onsets = detect_onsets(student, SR)
    alignment = align(reference, SR, student, SR)
    result = compare_rhythm(ref_onsets, student_onsets, alignment)
    assert len(result.points) >= 3
    assert result.mean_absolute_timing_offset < 0.2


def test_compare_rhythm_flags_missed_note():
    reference = _make_sequence([0.5, 0.5, 0.5, 0.5])
    student = _make_sequence([0.5, 0.5, 0.5], freqs=[NOTE_FREQS[0], NOTE_FREQS[1], NOTE_FREQS[3]])
    ref_onsets = detect_onsets(reference, SR)
    student_onsets = detect_onsets(student, SR)
    alignment = align(reference, SR, student, SR)
    result = compare_rhythm(ref_onsets, student_onsets, alignment)
    assert result.unmatched_reference_onsets >= 1
