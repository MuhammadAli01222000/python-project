"""
Custom exception classes for media cleaner application.
Follows clean error handling patterns and user-friendly error propagation.
"""

class CleanerError(Exception):
    """Base exception for all cleaner errors."""
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        return {
            "error": self.message,
            "details": self.details
        }


class UnsupportedFormatError(CleanerError):
    """Raised when an uploaded file format is not supported."""
    pass


class CorruptedFileError(CleanerError):
    """Raised when media file cannot be opened or decoded."""
    pass


class ProcessingError(CleanerError):
    """Raised when an error occurs during image or video inpainting."""
    pass


class TaskNotFoundError(CleanerError):
    """Raised when requested task ID does not exist."""
    pass
