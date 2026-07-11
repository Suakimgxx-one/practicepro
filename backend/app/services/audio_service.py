from pathlib import Path

import anyio
import librosa

from app.core.exceptions import InvalidAudioError


def _probe_sync(path: str) -> float:
    """
    Actually decodes the audio (not just reading a header) to confirm the
    file is real, playable audio — catches truncated uploads, misnamed
    non-audio files, and corrupt encodes that a header-only check would
    miss. librosa.load uses ffmpeg as a backend for compressed formats
    (mp3/m4a), which is why the Dockerfile installs it.
    """
    try:
        waveform, sample_rate = librosa.load(path, sr=None, mono=True)
    except Exception as e:
        raise InvalidAudioError(str(e)) from e

    if len(waveform) == 0:
        raise InvalidAudioError("decoded audio contains zero samples")

    return len(waveform) / sample_rate


async def probe_duration(path: Path) -> float:
    """
    Runs the blocking librosa decode in a worker thread so it doesn't
    block the async event loop — this is a synchronous, CPU-bound
    operation being called from an async route handler.
    """
    return await anyio.to_thread.run_sync(_probe_sync, str(path))
