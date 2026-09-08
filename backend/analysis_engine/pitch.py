from dataclasses import dataclass, field

import librosa
import numpy as np

from analysis_engine.alignment import AlignmentResult
from analysis_engine.features import HOP_LENGTH


@dataclass
class PitchContour:
    times: np.ndarray
    frequencies_hz: np.ndarray
    voiced: np.ndarray


def extract_pitch_contour(waveform, sr, hop_length=HOP_LENGTH, fmin=None, fmax=None):
    fmin = fmin or librosa.note_to_hz("C2")
    fmax = fmax or librosa.note_to_hz("C7")
    f0, voiced_flag, _voiced_prob = librosa.pyin(y=waveform, fmin=fmin, fmax=fmax, sr=sr, hop_length=hop_length)
    times = librosa.times_like(f0, sr=sr, hop_length=hop_length)
    return PitchContour(times=times, frequencies_hz=f0, voiced=voiced_flag)


@dataclass
class PitchDeviationPoint:
    reference_time: float
    student_time: float
    reference_hz: float
    student_hz: float
    cents_deviation: float


@dataclass
class PitchComparisonResult:
    points: list = field(default_factory=list)

    @property
    def mean_absolute_cents_deviation(self):
        if not self.points:
            return 0.0
        return float(np.mean([abs(p.cents_deviation) for p in self.points]))

    def flagged_regions(self, threshold_cents=25.0, max_gap_seconds=0.3):
        regions = []
        current_start = None
        last_time = None
        for point in self.points:
            flagged = abs(point.cents_deviation) > threshold_cents
            if flagged:
                if current_start is None:
                    current_start = point.reference_time
                elif last_time is not None and (point.reference_time - last_time) > max_gap_seconds:
                    regions.append((current_start, last_time))
                    current_start = point.reference_time
                last_time = point.reference_time
            else:
                if current_start is not None and last_time is not None:
                    regions.append((current_start, last_time))
                current_start = None
                last_time = None
        if current_start is not None and last_time is not None:
            regions.append((current_start, last_time))
        return regions


def compare_pitch(reference, student, alignment, max_time_gap=0.15):
    student_voiced_times = student.times[student.voiced]
    student_voiced_hz = student.frequencies_hz[student.voiced]
    points = []
    if len(student_voiced_times) == 0:
        return PitchComparisonResult(points=points)
    for t_ref, f_ref, is_voiced in zip(reference.times, reference.frequencies_hz, reference.voiced):
        if not is_voiced:
            continue
        target_student_time = alignment.reference_to_student(float(t_ref))
        idx = int(np.searchsorted(student_voiced_times, target_student_time))
        candidate_indices = [i for i in (idx - 1, idx) if 0 <= i < len(student_voiced_times)]
        if not candidate_indices:
            continue
        best_idx = min(candidate_indices, key=lambda i: abs(student_voiced_times[i] - target_student_time))
        if abs(student_voiced_times[best_idx] - target_student_time) > max_time_gap:
            continue
        f_student = student_voiced_hz[best_idx]
        cents = 1200.0 * np.log2(f_student / f_ref)
        points.append(PitchDeviationPoint(
            reference_time=float(t_ref), student_time=float(student_voiced_times[best_idx]),
            reference_hz=float(f_ref), student_hz=float(f_student), cents_deviation=float(cents),
        ))
    return PitchComparisonResult(points=points)
