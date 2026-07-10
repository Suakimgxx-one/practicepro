class NotFoundError(Exception):
    """Raised when a requested resource doesn't exist."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")
