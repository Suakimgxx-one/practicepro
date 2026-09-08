from dataclasses import dataclass, field

import numpy as np
import pyloudnorm as pyln

from analysis_engine.alignment import AlignmentResult

DEFAULT_FRAME_SECONDS = 0.4
DEFAULT_HOP_SECONDS = 0.1


@dataclass
class LoudnessContour:
    times: np.ndarray
    loudness_db: np.ndarray


def extract_loudness_contour(waveform, sr, frame_seconds=DEFAULT_FRAME_SECONDS, hop_seconds=DEFAULT_HOP_SECONDS):
    meter = pyln.Meter(sr, block_size=frame_seconds)
    frame_samples = int(frame_seconds * sr)
    hop_samples = int(hop_seconds * sr)
    times = []
    loudness_values = []
    start = 0
    while start + frame_samples <= len(waveform):
        window = waveform[start:start + frame_samples]
        try:
            loudness = meter.integrated_loudness(window)
        except Exception:
            loudness = float("-inf")
        if not np.isfinite(loudness):
            loudness = float("nan")
        center_time = (start + frame_samples / 2) / sr
        times.append(center_time)
        loudness_values.append(loudness)
        start += hop_samples
    return LoudnessContour(times=np.array(times), loudness_db=np.array(loudness_values))


@dataclass
class DynamicsDeviationPoint:
    reference_time: float
    student_time: float
    reference_loudness_db: float
    student_loudness_db: float
    loudness_difference_db: float


@dataclass
class DynamicsComparisonResult:
    points: list = field(default_factory=list)

    @property
    def mean_absolute_loudness_difference(self):
        if not self.points:
            return 0.0
        return float(np.mean([abs(p.loudness_difference_db) for p in self.points]))

    def flagged_regions(self, threshold_db=4.0, max_gap_seconds=1.0):
        regions = []
        current_start = None
        current_label = None
        last_time = None
        for point in self.points:
            if point.loudness_difference_db > threshold_db:
                label = "louder_than_reference"
            elif point.loudness_difference_db < -threshold_db:
                label = "quieter_than_reference"
            else:
                label = None
            if label is not None:
                breaks_region = (current_start is None or label != current_label or (last_time is not None and point.reference_time - last_time > max_gap_seconds))
                if breaks_region:
                    if current_start is not None and last_time is not None and current_label:
                        regions.append((current_start, last_time, current_label))
                    current_start = point.reference_time
                    current_label = label
                last_time = point.reference_time
            else:
                if current_start is not None and last_time is not None and current_label:
                    regions.append((current_start, last_time, current_label))
                current_start = None
                current_label = None
                last_time = None
        if current_start is not None and last_time is not None and current_label:
            regions.append((current_start, last_time, current_label))
        return regions


def compare_dynamics(reference, student, alignment, max_time_gap=0.3):
    valid_mask = ~np.isnan(student.loudness_db)
    student_times_valid = student.times[valid_mask]
    student_loudness_valid = student.loudness_db[valid_mask]
    points = []
    if len(student_times_valid) == 0:
        return DynamicsComparisonResult(points=points)
    for t_ref, ref_loudness in zip(reference.times, reference.loudness_db):
        if np.isnan(ref_loudness):
            continue
        target_time = alignment.reference_to_student(float(t_ref))
        idx = int(np.searchsorted(student_times_valid, target_time))
        candidate_indices = [i for i in (idx - 1, idx) if 0 <= i < len(student_times_valid)]
        if not candidate_indices:
            continue
        best_idx = min(candidate_indices, key=lambda i: abs(student_times_valid[i] - target_time))
        if abs(student_times_valid[best_idx] - target_time) > max_time_gap:
            continue
        student_loudness = float(student_loudness_valid[best_idx])
        difference = student_loudness - float(ref_loudness)
        points.append(DynamicsDeviationPoint(
            reference_time=float(t_ref), student_time=float(student_times_valid[best_idx]),
            reference_loudness_db=float(ref_loudness), student_loudness_db=student_loudness,
            loudness_difference_db=difference,
        ))
    return DynamicsComparisonResult(points=points)
