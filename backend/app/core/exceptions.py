class NotFoundError(Exception):
    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")


class UnsupportedFileTypeError(Exception):
    def __init__(self, extension: str, allowed: set[str]):
        self.extension = extension
        self.allowed = allowed
        super().__init__(f"File type '{extension}' is not supported. Allowed: {sorted(allowed)}")


class FileTooLargeError(Exception):
    def __init__(self, max_size_mb: int):
        self.max_size_mb = max_size_mb
        super().__init__(f"File exceeds the {max_size_mb}MB upload limit")


class InvalidAudioError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"File is not valid audio: {reason}")


class RecordingConflictError(Exception):
    def __init__(self, recording_id: str):
        self.recording_id = recording_id
        super().__init__(f"Recording '{recording_id}' already has audio uploaded")
