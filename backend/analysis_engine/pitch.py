from dataclasses import dataclass, field

import librosa
import numpy as np

from analysis_engine.alignment import AlignmentResult
from analysis_engine.features import HOP_LENGTH


@dataclass
class PitchContour:
    """
    Frame-by-frame pitch (F0, fundamental frequency) over the duration
    of a single recording. frequencies_hz is NaN wherever the frame
    was judged unvoiced (rests, breaths, noise) — pitch is only
    meaningful where a note is actually sounding.
    """

    times: np.ndarray
    frequencies_hz: np.ndarray
    voiced: np.ndarray


def extract_pitch_contour(
    waveform: np.ndarray,
    sr: int,
    hop_length: int = HOP_LENGTH,
    fmin: float | None = None,
    fmax: float | None = None,
) -> PitchContour:
    """
    Extracts a pitch contour using pYIN (probabilistic YIN) — a
    well-established autocorrelation-based pitch tracker with a
    voiced/unvoiced decision built in, which matters for real
    recordings that include rests and breaths, not just continuous
    tone. Default fmin/fmax (C2-C7) cover essentially the full range
    of most orchestral/band instruments and voice.
    """
    fmin = fmin or librosa.note_to_hz("C2")
    fmax = fmax or librosa.note_to_hz("C7")

    f0, voiced_flag, _voiced_prob = librosa.pyin(
        y=waveform, fmin=fmin, fmax=fmax, sr=sr, hop_length=hop_length
    )
    times = librosa.times_like(f0, sr=sr, hop_length=hop_length)

    return PitchContour(times=times, frequencies_hz=f0, voiced=voiced_flag)


@dataclass
class PitchDeviationPoint:
    """One comparison point: what the reference was doing, what the
    student was doing at the corresponding (DTW-aligned) moment, and
    the difference in cents. Positive = student sharp; negative =
    student flat. (100 cents = one semitone.)"""

    reference_time: float
    student_time: float
    reference_hz: float
    student_hz: float
    cents_deviation: float


@dataclass
class PitchComparisonResult:
    points: list[PitchDeviationPoint] = field(default_factory=list)

    @property
    def mean_absolute_cents_deviation(self) -> float:
        if not self.points:
            return 0.0
        return float(np.mean([abs(p.cents_deviation) for p in self.points]))

    def flagged_regions(
        self, threshold_cents: float = 25.0, max_gap_seconds: float = 0.3
    ) -> list[tuple[float, float]]:
        """
        Groups consecutive out-of-tune points into contiguous
        (start_time, end_time) regions in reference-time — this is
        what turns a mass of per-frame numbers into something like
        "sharp from 0:42 to 0:47", which is what a feedback message
        actually needs.
        """
        regions: list[tuple[float, float]] = []
        current_start: float | None = None
        last_time: float | None = None

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


def compare_pitch(
    reference: PitchContour,
    student: PitchContour,
    alignment: AlignmentResult,
    max_time_gap: float = 0.15,
) -> PitchComparisonResult:
    """
    For every voiced reference frame, finds where that moment falls in
    the student's timeline (via the DTW alignment), then finds the
    nearest voiced student frame to that target time and compares
    pitch in cents.

    Deliberately does NOT interpolate the student's pitch curve across
    time — pitch is undefined during silence/unvoiced frames, so
    interpolating across a gap would fabricate a note that was never
    played. Instead we do a nearest-neighbor lookup and simply skip
    the comparison (rather than guess) if the nearest voiced student
    frame is further than max_time_gap away, which usually means the
    student wasn't playing anything comparable at that moment (e.g. a
    rest, or a passage they skipped).
    """
    student_voiced_times = student.times[student.voiced]
    student_voiced_hz = student.frequencies_hz[student.voiced]

    points: list[PitchDeviationPoint] = []

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

        best_idx = min(
            candidate_indices, key=lambda i: abs(student_voiced_times[i] - target_student_time)
        )
        if abs(student_voiced_times[best_idx] - target_student_time) > max_time_gap:
            continue

        f_student = student_voiced_hz[best_idx]
        cents = 1200.0 * np.log2(f_student / f_ref)

        points.append(
            PitchDeviationPoint(
                reference_time=float(t_ref),
                student_time=float(student_voiced_times[best_idx]),
                reference_hz=float(f_ref),
                student_hz=float(f_student),
                cents_deviation=float(cents),
            )
        )

    return PitchComparisonResult(points=points)
