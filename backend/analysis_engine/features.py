import librosa
import numpy as np

DEFAULT_SR = 22050
HOP_LENGTH = 512


def load_audio(path: str, sr: int = DEFAULT_SR) -> tuple[np.ndarray, int]:
    """Loads an audio file to mono at a fixed sample rate, so every
    downstream computation (frame timing, feature extraction) is
    working with consistent, comparable units regardless of the
    original file's format or sample rate."""
    waveform, sample_rate = librosa.load(path, sr=sr, mono=True)
    return waveform, sample_rate


def chroma_features(waveform: np.ndarray, sr: int, hop_length: int = HOP_LENGTH) -> np.ndarray:
    """
    Chroma features collapse audio into 12 bins representing pitch
    class (C, C#, D, ... regardless of octave) at each time frame.

    This is deliberately *not* the raw waveform or a full spectrogram:
    for alignment purposes we want two frames to look "similar" when
    the same notes are being played, independent of which octave,
    which instrument, or how loud — those differences are exactly what
    later milestones (pitch/dynamics comparison) want to measure, so
    the alignment step itself needs to be blind to them.

    chroma_cqt (constant-Q transform) is used over the simpler
    chroma_stft because its frequency bins are spaced logarithmically,
    matching how musical pitch actually works — this makes pitch-class
    separation meaningfully cleaner than a linear-frequency STFT,
    at the cost of being somewhat slower to compute.
    """
    return librosa.feature.chroma_cqt(y=waveform, sr=sr, hop_length=hop_length)
