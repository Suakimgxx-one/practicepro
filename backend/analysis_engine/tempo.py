from dataclasses import dataclass, field

import librosa
import numpy as np

from analysis_engine.alignment import AlignmentResult


@dataclass
class TempoRatioPoint:
    reference_time: float
    local_tempo_ratio: float


@dataclass
class TempoComparisonResult:
    points: list[TempoRatioPoint] = field(default_factory=list)
    reference_average_bpm: float | None = None
    student_average_bpm: float | None = None

    @property
    def mean_tempo_ratio(self) -> float:
        if not self.points:
            return 1.0
        return float(np.mean([p.local_tempo_ratio for p in self.points]))

    def flagged_regions(self, ratio_threshold: float = 0.15, max_gap_seconds: float = 1.0) -> list[tuple[float, float, str]]:
        regions: list[tuple[float, float, str]] = []
        current_start: float | None = None
        current_label: str | None = None
        last_time: float | None = None
        for point in self.points:
            deviation = point.local_tempo_ratio - 1.0
            if deviation > ratio_threshold:
                label: str | None = "dragging"
            elif deviation < -ratio_threshold:
                label = "rushing"
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


def compute_tempo_ratio_curve(alignment: AlignmentResult, sample_interval: float = 0.25) -> list[TempoRatioPoint]:
    if len(alignment.reference_times) < 2:
        return []
    ref_start = float(alignment.reference_times[0])
    ref_end = float(alignment.reference_times[-1])
    if ref_end <= ref_start:
        return []
    sample_times = np.arange(ref_start, ref_end, sample_interval)
    if len(sample_times) < 2:
        sample_times = np.linspace(ref_start, ref_end, 5)
    student_sample_times = np.array([alignment.reference_to_student(t) for t in sample_times])
    points: list[TempoRatioPoint] = []
    for i in range(len(sample_times) - 1):
        d_ref = sample_times[i + 1] - sample_times[i]
        if d_ref <= 0:
            continue
        d_student = student_sample_times[i + 1] - student_sample_times[i]
        ratio = d_student / d_ref
        midpoint = (sample_times[i] + sample_times[i + 1]) / 2
        points.append(TempoRatioPoint(reference_time=float(midpoint), local_tempo_ratio=float(ratio)))
    return points


def estimate_average_bpm(waveform: np.ndarray, sr: int) -> float | None:
    try:
        tempo, _beat_frames = librosa.beat.beat_track(y=waveform, sr=sr)
        bpm = float(tempo) if np.isscalar(tempo) else float(np.asarray(tempo).flat[0])
    except Exception:
        return None
    if bpm <= 0:
        return None
    return bpm


def compare_tempo(reference_waveform: np.ndarray, reference_sr: int, student_waveform: np.ndarray, student_sr: int, alignment: AlignmentResult, sample_interval: float = 0.25) -> TempoComparisonResult:
    points = compute_tempo_ratio_curve(alignment, sample_interval=sample_interval)
    reference_bpm = estimate_average_bpm(reference_waveform, reference_sr)
    student_bpm = estimate_average_bpm(student_waveform, student_sr)
    return TempoComparisonResult(points=points, reference_average_bpm=reference_bpm, student_average_bpm=student_bpm)
