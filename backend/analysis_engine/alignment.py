from dataclasses import dataclass

import librosa
import numpy as np

from analysis_engine.features import HOP_LENGTH, chroma_features


@dataclass
class AlignmentResult:
    """
    The warping path between a reference and student performance,
    expressed as parallel arrays of timestamps: reference_times[i] and
    student_times[i] are "the same musical moment," just at potentially
    different points in each recording's own timeline.

    `cost` is the total accumulated DTW distance — lower means the two
    performances' note sequences matched more closely overall. It's a
    rough similarity signal, not a musical-quality score by itself
    (e.g. it doesn't know or care about intonation or dynamics).
    """

    reference_times: np.ndarray
    student_times: np.ndarray
    cost: float

    def reference_to_student(self, t: float) -> float:
        """Maps a timestamp in the reference recording to the
        corresponding timestamp in the student recording, by linear
        interpolation along the warping path. This is the function
        every later comparison (pitch/rhythm/dynamics) will use to ask
        "what was the student doing at the moment corresponding to
        reference time t?"."""
        return float(np.interp(t, self.reference_times, self.student_times))

    def student_to_reference(self, t: float) -> float:
        """Inverse of reference_to_student. DTW allows one reference
        frame to map to several student frames (e.g. a held/dragged
        note), so student_times isn't guaranteed strictly increasing
        point-to-point — we sort by student_times first so np.interp's
        requirement of an increasing x-array holds."""
        order = np.argsort(self.student_times)
        return float(np.interp(t, self.student_times[order], self.reference_times[order]))


def align(
    reference_waveform: np.ndarray,
    reference_sr: int,
    student_waveform: np.ndarray,
    student_sr: int,
    hop_length: int = HOP_LENGTH,
) -> AlignmentResult:
    """
    Aligns a student performance to a reference performance using
    Dynamic Time Warping over chroma features.

    Why DTW instead of a simple linear time-stretch: two performances
    of the same piece rarely share one global tempo ratio — a student
    might rush one phrase and drag another. A linear stretch can only
    correct for a single constant ratio across the whole piece. DTW
    instead finds a nonlinear (but monotonic — time can't run
    backwards), least-cost alignment between the two time axes,
    independently accounting for tempo drift at every point in the
    piece rather than just at the start and end.
    """
    ref_chroma = chroma_features(reference_waveform, reference_sr, hop_length)
    student_chroma = chroma_features(student_waveform, student_sr, hop_length)

    cost_matrix, warping_path = librosa.sequence.dtw(X=ref_chroma, Y=student_chroma, metric="cosine")

    # librosa returns the path in reverse (end -> start); flip to chronological order
    warping_path = warping_path[::-1]

    reference_frames = warping_path[:, 0]
    student_frames = warping_path[:, 1]

    reference_times = librosa.frames_to_time(reference_frames, sr=reference_sr, hop_length=hop_length)
    student_times = librosa.frames_to_time(student_frames, sr=student_sr, hop_length=hop_length)

    total_cost = float(cost_matrix[-1, -1])

    return AlignmentResult(
        reference_times=reference_times,
        student_times=student_times,
        cost=total_cost,
    )
