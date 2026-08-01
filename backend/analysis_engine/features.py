import librosa
import numpy as np

DEFAULT_SR = 22050
HOP_LENGTH = 512


def load_audio(path: str, sr: int = DEFAULT_SR) -> tuple[np.ndarray, int]:
    waveform, sample_rate = librosa.load(path, sr=sr, mono=True)
    return waveform, sample_rate


def chroma_features(waveform: np.ndarray, sr: int, hop_length: int = HOP_LENGTH) -> np.ndarray:
    return librosa.feature.chroma_cqt(y=waveform, sr=sr, hop_length=hop_length)
