import numpy as np
import pytest

from analysis_engine.alignment import align
from analysis_engine.pitch import compare_pitch, extract_pitch_contour

SR = 22050


def _tone(freq: float, duration: float, sr: int = SR) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    waveform = 0.3 * np.sin(2 * np.pi * freq * t)

    fade_samples = int(sr * 0.01)
    if fade_samples > 0 and len(waveform) > 2 * fade_samples:
        envelope = np.ones_like(waveform)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        waveform = waveform * envelope

    return waveform


def _cents_shift(freq: float, cents: float) -> float:
    """Shifts a frequency by a given number of cents (100 cents = 1 semitone)."""
    return freq * (2 ** (cents / 1200))


def test_extract_pitch_contour_detects_correct_frequency():
    """A pure 440Hz tone should be detected as ~440Hz (A4) across
    essentially all voiced frames."""
    waveform = _tone(440.0, 1.0)
    contour = extract_pitch_contour(waveform, SR)

    voiced_freqs = contour.frequencies_hz[contour.voiced]
    assert len(voiced_freqs) > 0

    mean_freq = np.mean(voiced_freqs)
    assert mean_freq == pytest.approx(440.0, abs=3.0)


def test_extract_pitch_contour_marks_silence_unvoiced():
    """Silence should not be reported as a confident pitch."""
    silence = np.zeros(SR)  # 1 second of silence
    contour = extract_pitch_contour(silence, SR)

    # pYIN may still mark a few frames voiced on pure silence due to
    # numerical noise, but the overwhelming majority should be unvoiced.
    voiced_fraction = np.mean(contour.voiced)
    assert voiced_fraction < 0.2


def test_compare_pitch_identical_performance_shows_near_zero_deviation():
    waveform = _tone(440.0, 1.0)
    ref_contour = extract_pitch_contour(waveform, SR)
    student_contour = extract_pitch_contour(waveform, SR)
    alignment = align(waveform, SR, waveform, SR)

    result = compare_pitch(ref_contour, student_contour, alignment)

    assert len(result.points) > 0
    assert result.mean_absolute_cents_deviation < 5.0


def test_compare_pitch_detects_consistent_sharp_offset():
    """Student plays the whole piece 50 cents sharp — every comparison
    point should reflect a positive (sharp) deviation of roughly that
    size."""
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
    """First note in tune, second note sharp by 60 cents — the
    flagged region should correspond to roughly the second half of
    the piece, not the whole thing."""
    in_tune_freq = 440.0
    sharp_freq = _cents_shift(440.0, 60)

    reference_waveform = np.concatenate([_tone(in_tune_freq, 1.0), _tone(392.0, 1.0)])
    student_waveform = np.concatenate([_tone(in_tune_freq, 1.0), _tone(_cents_shift(392.0, 60), 1.0)])

    ref_contour = extract_pitch_contour(reference_waveform, SR)
    student_contour = extract_pitch_contour(student_waveform, SR)
    alignment = align(reference_waveform, SR, student_waveform, SR)

    result = compare_pitch(ref_contour, student_contour, alignment)
    regions = result.flagged_regions(threshold_cents=25.0)

    assert len(regions) >= 1
    # The flagged region should start somewhere around the second note
    # (t=1.0s), not at the very beginning.
    first_region_start = regions[0][0]
    assert first_region_start > 0.5
