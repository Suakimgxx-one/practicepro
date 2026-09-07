from dataclasses import dataclass, field

import librosa
import numpy as np

from analysis_engine.alignment import AlignmentResult
from analysis_engine.features import HOP_LENGTH


def detect_onsets(waveform: np.ndarray, sr: int, hop_length: int = HOP_LENGTH) -> np.ndarray:
    onset_times = librosa.onset.onset_detect(y=waveform, sr=sr, hop_length=hop_length, units="time", backtrack=True)
    return np.asarray(onset_times, dtype=float)


@dataclass
class RhythmDeviationPoint:
    reference_time: float
    predicted_student_time: float
    actual_student_time: float
    timing_offset_seconds: float


@dataclass
class RhythmComparisonResult:
    points: list[RhythmDeviationPoint] = field(default_factory=list)
    unmatched_reference_onsets: int = 0
    unmatched_student_onsets: int = 0

    @property
    def mean_absolute_timing_offset(self) -> float:
        if not self.points:
            return 0.0
        return float(np.mean([abs(p.timing_offset_seconds) for p in self.points]))

    @property
    def rushed_count(self) -> int:
        return sum(1 for p in self.points if p.timing_offset_seconds < -0.05)

    @property
    def dragged_count(self) -> int:
        return sum(1 for p in self.points if p.timing_offset_seconds > 0.05)

    def flagged_regions(self, threshold_seconds: float = 0.1, max_gap_seconds: float = 1.0) -> list[tuple[float, float]]:
        regions: list[tuple[float, float]] = []
        current_start: float | None = None
        last_time: float | None = None
        for point in self.points:
            flagged = abs(point.timing_offset_seconds) > threshold_seconds
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


def compare_rhythm(reference_onsets: np.ndarray, student_onsets: np.ndarray, alignment: AlignmentResult, max_match_gap: float = 0.3) -> RhythmComparisonResult:
    points: list[RhythmDeviationPoint] = []
    used_student_indices: set[int] = set()
    for t_ref in reference_onsets:
        predicted = alignment.reference_to_student(float(t_ref))
        available_indices = [i for i in range(len(student_onsets)) if i not in used_student_indices]
        if not available_indices:
            continue
        idx = min(available_indices, key=lambda i: abs(student_onsets[i] - predicted))
        actual = float(student_onsets[idx])
        if abs(actual - predicted) > max_match_gap:
            continue
        used_student_indices.add(idx)
        points.append(RhythmDeviationPoint(
            reference_time=float(t_ref), predicted_student_time=float(predicted),
            actual_student_time=actual, timing_offset_seconds=actual - predicted,
        ))
    unmatched_reference = len(reference_onsets) - len(points)
    unmatched_student = len(student_onsets) - len(used_student_indices)
    return RhythmComparisonResult(points=points, unmatched_reference_onsets=unmatched_reference, unmatched_student_onsets=unmatched_student)
