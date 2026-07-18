import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, UnsupportedFileTypeError

CHUNK_SIZE = 1024 * 1024


def validate_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in settings.ALLOWED_AUDIO_EXTENSIONS:
        raise UnsupportedFileTypeError(extension, settings.ALLOWED_AUDIO_EXTENSIONS)
    return extension


async def save_upload(recording_id: uuid.UUID, upload_file: UploadFile) -> Path:
    extension = validate_extension(upload_file.filename or "")

    recording_dir = Path(settings.LOCAL_STORAGE_PATH) / str(recording_id)
    recording_dir.mkdir(parents=True, exist_ok=True)
    destination = recording_dir / f"original{extension}"

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    bytes_written = 0

    try:
        with open(destination, "wb") as out_file:
            while chunk := await upload_file.read(CHUNK_SIZE):
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    raise FileTooLargeError(settings.MAX_UPLOAD_SIZE_MB)
                out_file.write(chunk)
    except FileTooLargeError:
        destination.unlink(missing_ok=True)
        raise

    return destination


def delete_file(path: Path) -> None:
    path.unlink(missing_ok=True)
    try:
        path.parent.rmdir()
    except OSError:
        pass
