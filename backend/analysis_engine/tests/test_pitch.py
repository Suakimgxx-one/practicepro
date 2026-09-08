import numpy as np
import pytest
from analysis_engine.alignment import align
from analysis_engine.pitch import compare_pitch, extract_pitch_contour

SR = 22050

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

def _cents_shift(freq, cents):
    return freq * (2 ** (cents / 1200))

def test_extract_pitch_contour_detects_correct_frequency():
    waveform = _tone(440.0, 1.0)
    contour = extract_pitch_contour(waveform, SR)
    voiced_freqs = contour.frequencies_hz[contour.voiced]
    assert len(voiced_freqs) > 0
    assert np.mean(voiced_freqs) == pytest.approx(440.0, abs=3.0)

def test_extract_pitch_contour_marks_silence_unvoiced():
    silence = np.zeros(SR)
    contour = extract_pitch_contour(silence, SR)
    assert np.mean(contour.voiced) < 0.2

def test_compare_pitch_identical_performance_shows_near_zero_deviation():
    waveform = _tone(440.0, 1.0)
    ref_contour = extract_pitch_contour(waveform, SR)
    student_contour = extract_pitch_contour(waveform, SR)
    alignment = align(waveform, SR, waveform, SR)
    result = compare_pitch(ref_contour, student_contour, alignment)
    assert len(result.points) > 0
    assert result.mean_absolute_cents_deviation < 5.0

def test_compare_pitch_detects_consistent_sharp_offset():
    reference_freq = 440.0
    student_freq = _cents_shift(reference_freq, 50)
    reference_waveform = _tone(reference_freq, 1.0)
    student_waveform = _tone(student_freq, 1.0)
    ref_contour = extract_pitch_contour(reference_waveform, SR)
    student_contour = extract_pitch_contour(student_waveform, SR)
    alignment = align(reference_waveform, SR, student_waveform, SR)
    result = compare_pitch(ref_contour, student_contour, alignment)
    assert len(result.points) > 0
    mean_deviation = np.mean([p.cents_deviation for p in result.points])
    assert mean_deviation == pytest.approx(50.0, abs=10.0)

def test_flagged_regions_identifies_only_the_out_of_tune_section():
    in_tune_freq = 440.0
    reference_waveform = np.concatenate([_tone(in_tune_freq, 1.0), _tone(392.0, 1.0)])
    student_waveform = np.concatenate([_tone(in_tune_freq, 1.0), _tone(_cents_shift(392.0, 60), 1.0)])
    ref_contour = extract_pitch_contour(reference_waveform, SR)
    student_contour = extract_pitch_contour(student_waveform, SR)
    alignment = align(reference_waveform, SR, student_waveform, SR)
    result = compare_pitch(ref_contour, student_contour, alignment)
    regions = result.flagged_regions(threshold_cents=25.0)
    assert len(regions) >= 1
    assert regions[0][0] > 0.5
