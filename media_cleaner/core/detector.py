"""
Text, watermark, numbers, and symbol detector module.
Generates binary masks for inpainting using morphological operations,
edge detection, color thresholding, and user-defined ROIs.
"""

from typing import Optional, Tuple, Dict
import numpy as np
import cv2

# Standard ROI presets (normalized ratios: x, y, width, height)
ROI_PRESETS: Dict[str, Tuple[float, float, float, float]] = {
    "bottom_right": (0.70, 0.85, 0.28, 0.13),     # Common watermark position (TikTok, CapCut, etc.)
    "bottom_left": (0.02, 0.85, 0.28, 0.13),      # Bottom left brand logos
    "top_right": (0.70, 0.02, 0.28, 0.13),        # TV channels & corner bugs
    "top_left": (0.02, 0.02, 0.28, 0.13),         # Channel identifiers
    "bottom_subtitles": (0.05, 0.82, 0.90, 0.16), # Full-width subtitle zone
    "top_banner": (0.05, 0.02, 0.90, 0.15),       # Top text banners
    "center": (0.25, 0.35, 0.50, 0.30),           # Center watermarks / samples
}


def create_blank_mask(shape: Tuple[int, ...]) -> np.ndarray:
    """Create a single-channel 8-bit black mask matching frame dimensions."""
    h, w = shape[:2]
    return np.zeros((h, w), dtype=np.uint8)


def get_preset_coordinates(
    frame_width: int,
    frame_height: int,
    preset_name: str
) -> Tuple[int, int, int, int]:
    """
    Calculate pixel coordinates (x, y, w, h) from a preset name.
    """
    if preset_name not in ROI_PRESETS:
        preset_name = "bottom_right"

    rx, ry, rw, rh = ROI_PRESETS[preset_name]
    x = int(rx * frame_width)
    y = int(ry * frame_height)
    w = int(rw * frame_width)
    h = int(rh * frame_height)

    # Clamp to boundaries
    x = max(0, min(x, frame_width - 1))
    y = max(0, min(y, frame_height - 1))
    w = max(1, min(w, frame_width - x))
    h = max(1, min(h, frame_height - y))

    return x, y, w, h


def create_roi_mask(
    frame_shape: Tuple[int, ...],
    x: int,
    y: int,
    w: int,
    h: int
) -> np.ndarray:
    """
    Create a binary mask filling the specified rectangular ROI.
    """
    mask = create_blank_mask(frame_shape)
    h_max, w_max = frame_shape[:2]

    # Boundary safety
    x1 = max(0, min(int(x), w_max))
    y1 = max(0, min(int(y), h_max))
    x2 = max(0, min(int(x + w), w_max))
    y2 = max(0, min(int(y + h), h_max))

    if x2 > x1 and y2 > y1:
        mask[y1:y2, x1:x2] = 255

    return mask


def detect_text_in_region(
    image_bgr: np.ndarray,
    sensitivity: int = 50,
    min_area: int = 6,
    max_area_ratio: float = 0.5
) -> np.ndarray:
    """
    Detect text, numbers, and symbols inside a BGR image patch using
    morphological gradients, adaptive thresholding, and contour filtering.

    Args:
        image_bgr: Input patch or whole image in BGR format.
        sensitivity: Sensitivity from 10 (strict) to 100 (aggressive).
        min_area: Minimum pixel area to keep as text character.
        max_area_ratio: Maximum area fraction of the patch to prevent masking background.

    Returns:
        Binary mask (uint8) where text/symbol pixels are 255.
    """
    h, w = image_bgr.shape[:2]
    total_pixels = h * w
    if total_pixels == 0:
        return np.zeros((h, w), dtype=np.uint8)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Morphological Gradient (highlights sharp transitions characteristic of text)
    kernel_size = 3 if sensitivity < 60 else 5
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)

    # 2. Adaptive / Otsu Thresholding
    thresh_val = max(10, int(255 * (1.0 - (sensitivity / 120.0))))
    _, binary_grad = cv2.threshold(gradient, thresh_val, 255, cv2.THRESH_BINARY)

    # 3. Edge detection supplement (Canny)
    low_thresh = max(20, int(150 - sensitivity))
    high_thresh = min(250, low_thresh * 2)
    edges = cv2.Canny(gray, low_thresh, high_thresh)

    # Combine gradient and edge evidence
    combined = cv2.bitwise_or(binary_grad, edges)

    # 4. Morphological close to bridge adjacent letter strokes
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, close_kernel)

    # 5. Connected components filter: eliminate whole-background blobs or single-pixel noise
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    final_mask = np.zeros_like(gray)

    max_allowed_area = int(total_pixels * max_area_ratio)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]

        # Ignore tiny speckles
        if area < min_area:
            continue

        # Ignore gigantic bounding boxes that consume the entire frame
        if area > max_allowed_area and (bw > w * 0.95 and bh > h * 0.95):
            continue

        final_mask[labels == i] = 255

    return final_mask


def detect_bright_watermark(
    image_bgr: np.ndarray,
    threshold: int = 200
) -> np.ndarray:
    """
    Detect white / high-luminance subtitles or translucent watermarks.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    s_channel = hsv[:, :, 1]

    # High brightness, low saturation (typical white/gray subtitles)
    _, bright_mask = cv2.threshold(v_channel, threshold, 255, cv2.THRESH_BINARY)
    _, low_sat_mask = cv2.threshold(s_channel, 60, 255, cv2.THRESH_BINARY_INV)

    return cv2.bitwise_and(bright_mask, low_sat_mask)


def build_cleaning_mask(
    image_bgr: np.ndarray,
    mode: str = "roi_auto",
    roi: Optional[Tuple[int, int, int, int]] = None,
    preset: Optional[str] = None,
    sensitivity: int = 60,
    custom_mask: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Unified mask generator supporting multiple detection workflows (DRY pattern).

    Modes:
        - 'custom': User directly provided drawn brush mask.
        - 'roi_box': Entire ROI box is replaced/inpainted (fastest & robust for corner logos).
        - 'roi_auto': Only text/symbols inside the specified ROI are detected and masked.
        - 'preset_box': Entire preset box is inpainted.
        - 'preset_auto': Text/symbols inside a standard preset zone are detected.
        - 'full_auto': Automatic text/symbol detection across the entire frame.

    Args:
        image_bgr: Input BGR image.
        mode: Detection strategy.
        roi: (x, y, w, h) coordinates if applicable.
        preset: Name of preset (e.g. 'bottom_right', 'bottom_subtitles').
        sensitivity: Detection sensitivity (10-100).
        custom_mask: Optional pre-drawn 2D binary mask.

    Returns:
        Binary mask (uint8) ready for inpainter.
    """
    h, w = image_bgr.shape[:2]

    # 1. Custom mask provided directly by user (e.g. interactive canvas brush)
    if custom_mask is not None and mode == "custom":
        if custom_mask.shape[:2] != (h, w):
            return cv2.resize(custom_mask, (w, h), interpolation=cv2.INTER_NEAREST)
        return (custom_mask > 0).astype(np.uint8) * 255

    # 2. Determine target ROI
    target_roi = None
    if mode in ("roi_box", "roi_auto") and roi is not None:
        target_roi = roi
    elif mode in ("preset_box", "preset_auto") or (preset is not None and preset in ROI_PRESETS):
        target_roi = get_preset_coordinates(w, h, preset or "bottom_right")

    # 3. Entire Box mode (Replace the whole bounding region)
    if mode in ("roi_box", "preset_box"):
        if target_roi is None:
            target_roi = get_preset_coordinates(w, h, "bottom_right")
        rx, ry, rw, rh = target_roi
        return create_roi_mask((h, w), rx, ry, rw, rh)

    # 4. Text/Symbol Detection within ROI
    if mode in ("roi_auto", "preset_auto") and target_roi is not None:
        rx, ry, rw, rh = target_roi
        # Clamp coordinates
        rx1 = max(0, min(rx, w - 1))
        ry1 = max(0, min(ry, h - 1))
        rx2 = max(0, min(rx + rw, w))
        ry2 = max(0, min(ry + rh, h))

        if rx2 <= rx1 or ry2 <= ry1:
            return create_blank_mask((h, w))

        patch = image_bgr[ry1:ry2, rx1:rx2]
        text_patch_mask = detect_text_in_region(patch, sensitivity=sensitivity)
        bright_patch_mask = detect_bright_watermark(patch)

        patch_mask = cv2.bitwise_or(text_patch_mask, bright_patch_mask)

        # If very few text pixels found in the chosen box, fallback to box mask
        # to ensure user's selected logo is cleaned
        if np.sum(patch_mask > 0) < 15:
            patch_mask = np.full(patch.shape[:2], 255, dtype=np.uint8)

        full_mask = create_blank_mask((h, w))
        full_mask[ry1:ry2, rx1:rx2] = patch_mask
        return full_mask

    # 5. Full frame automatic detection
    text_mask = detect_text_in_region(image_bgr, sensitivity=sensitivity)
    bright_mask = detect_bright_watermark(image_bgr)
    return cv2.bitwise_or(text_mask, bright_mask)
