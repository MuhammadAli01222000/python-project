"""
Core cleaning and processing package.
"""

from .exceptions import (
    CleanerError,
    UnsupportedFormatError,
    CorruptedFileError,
    ProcessingError,
    TaskNotFoundError,
)
from .detector import (
    build_cleaning_mask,
    create_roi_mask,
    get_preset_coordinates,
    ROI_PRESETS,
)
from .inpainter import inpaint_frame, dilate_mask
from .image_processor import ImageProcessor
from .video_processor import VideoProcessor

__all__ = [
    "CleanerError",
    "UnsupportedFormatError",
    "CorruptedFileError",
    "ProcessingError",
    "TaskNotFoundError",
    "build_cleaning_mask",
    "create_roi_mask",
    "get_preset_coordinates",
    "ROI_PRESETS",
    "inpaint_frame",
    "dilate_mask",
    "ImageProcessor",
    "VideoProcessor",
]
