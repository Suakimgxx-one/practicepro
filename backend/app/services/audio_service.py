from pathlib import Path

import anyio
import librosa

from app.core.exceptions import InvalidAudioError


def probe_duration_sync(path: str) -> float:
    try:
        waveform, sample_rate = librosa.load(path, sr=None, mono=True)
    except Exception as e:
        raise InvalidAudioError(str(e)) from e

    if len(waveform) == 0:
        raise InvalidAudioError("decoded audio contains zero samples")

    return len(waveform) / sample_rate


async def probe_duration(path: Path) -> float:
    return await anyio.to_thread.run_sync(probe_duration_sync, str(path))
