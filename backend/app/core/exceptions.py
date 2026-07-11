class NotFoundError(Exception):
    """Raised when a requested resource doesn't exist."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")


class UnsupportedFileTypeError(Exception):
    """Raised when an uploaded file's extension isn't in the allowlist."""

    def __init__(self, extension: str, allowed: set[str]):
        self.extension = extension
        self.allowed = allowed
        super().__init__(
            f"File type '{extension}' is not supported. Allowed: {sorted(allowed)}"
        )


class FileTooLargeError(Exception):
    """Raised when an uploaded file exceeds the configured size limit."""

    def __init__(self, max_size_mb: int):
        self.max_size_mb = max_size_mb
        super().__init__(f"File exceeds the {max_size_mb}MB upload limit")


class InvalidAudioError(Exception):
    """
    Raised when a file has an allowed extension but isn't actually
    decodable audio (corrupt, truncated, or misnamed non-audio content).
    """

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"File is not valid audio: {reason}")


class RecordingConflictError(Exception):
    """Raised when trying to upload to a recording that's already ready."""

    def __init__(self, recording_id: str):
        self.recording_id = recording_id
        super().__init__(f"Recording '{recording_id}' already has audio uploaded")
