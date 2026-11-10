"""
Inpainting engine module.
Performs lightweight, high-performance inpainting using OpenCV's Telea
and Navier-Stokes algorithms, augmented with edge feathering and dilation.
"""

from typing import Literal
import numpy as np
import cv2


def dilate_mask(mask: np.ndarray, iterations: int = 2) -> np.ndarray:
    """
    Dilate mask boundaries slightly so edge artifacts of letters/logos are fully covered.
    """
    if iterations <= 0:
        return mask

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.dilate(mask, kernel, iterations=iterations)


def inpaint_frame(
    image_bgr: np.ndarray,
    mask: np.ndarray,
    method: Literal["telea", "ns"] = "telea",
    inpaint_radius: int = 3,
    dilate_iterations: int = 2,
    smooth_edges: bool = True
) -> np.ndarray:
    """
    Inpaint/remove masked regions from an image or video frame.

    Args:
        image_bgr: Source image in BGR (uint8).
        mask: Single-channel binary mask (uint8) where 255 = region to remove.
        method: 'telea' (Fast Marching Method) or 'ns' (Navier-Stokes fluid dynamics).
        inpaint_radius: Neighborhood radius around inpainting pixels.
        dilate_iterations: Number of dilation iterations to expand mask coverage.
        smooth_edges: Whether to feather inpaint boundaries for seamless blending.

    Returns:
        Cleaned BGR image.
    """
    if mask is None or np.count_nonzero(mask) == 0:
        return image_bgr.copy()

    # Ensure mask is single channel uint8
    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    mask = (mask > 0).astype(np.uint8) * 255

    # 1. Dilate mask to engulf border pixels
    dilated = dilate_mask(mask, iterations=dilate_iterations)

    # 2. Choose algorithm
    flags = cv2.INPAINT_TELEA if method.lower() == "telea" else cv2.INPAINT_NS
    radius = max(1, min(int(inpaint_radius), 25))

    # 3. Fast inpaint
    inpainted = cv2.inpaint(image_bgr, dilated, inpaintRadius=radius, flags=flags)

    # 4. Optional edge smoothing / feathering
    if smooth_edges and dilate_iterations > 0:
        # Create a soft transition mask along the outer border of the dilated mask
        border_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated_more = cv2.dilate(dilated, border_kernel, iterations=1)
        border_zone = cv2.subtract(dilated_more, dilated)

        if np.count_nonzero(border_zone) > 0:
            blurred_inpaint = cv2.GaussianBlur(inpainted, (3, 3), 0)
            alpha = (border_zone.astype(np.float32) / 255.0)[:, :, np.newaxis]
            inpainted = (inpainted * (1.0 - alpha * 0.5) + blurred_inpaint * (alpha * 0.5)).astype(np.uint8)

    return inpainted
