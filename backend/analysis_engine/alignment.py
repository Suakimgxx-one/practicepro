from dataclasses import dataclass

import librosa
import numpy as np

from analysis_engine.features import HOP_LENGTH, chroma_features


@dataclass
class AlignmentResult:
    reference_times: np.ndarray
    student_times: np.ndarray
    cost: float

    def reference_to_student(self, t: float) -> float:
        return float(np.interp(t, self.reference_times, self.student_times))

    def student_to_reference(self, t: float) -> float:
        order = np.argsort(self.student_times)
        return float(np.interp(t, self.student_times[order], self.reference_times[order]))


def align(reference_waveform, reference_sr, student_waveform, student_sr, hop_length=HOP_LENGTH):
    ref_chroma = chroma_features(reference_waveform, reference_sr, hop_length)
    student_chroma = chroma_features(student_waveform, student_sr, hop_length)
    cost_matrix, warping_path = librosa.sequence.dtw(X=ref_chroma, Y=student_chroma, metric="cosine")
    warping_path = warping_path[::-1]
    reference_frames = warping_path[:, 0]
    student_frames = warping_path[:, 1]
    reference_times = librosa.frames_to_time(reference_frames, sr=reference_sr, hop_length=hop_length)
    student_times = librosa.frames_to_time(student_frames, sr=student_sr, hop_length=hop_length)
    total_cost = float(cost_matrix[-1, -1])
    return AlignmentResult(reference_times=reference_times, student_times=student_times, cost=total_cost)
