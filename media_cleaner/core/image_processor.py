"""
Image cleaning processor.
Handles decoding (with EXIF auto-orientation), cleaning pipeline, and saving.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import numpy as np
import cv2
from PIL import Image, ImageOps

from .detector import build_cleaning_mask
from .inpainter import inpaint_frame
from .exceptions import CorruptedFileError, ProcessingError


class ImageProcessor:
    """Processes still images to remove watermarks, subtitles, text, and logos."""

    @staticmethod
    def load_image(file_path: Path) -> np.ndarray:
        """
        Load image safely using Pillow to preserve correct EXIF orientation,
        then convert to BGR OpenCV format.
        """
        try:
            with Image.open(file_path) as pil_img:
                # Correct orientation based on EXIF tag (avoids rotated smartphone photos)
                pil_img = ImageOps.exif_transpose(pil_img)
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                rgb_arr = np.array(pil_img)
                bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
                return bgr_arr
        except Exception as e:
            raise CorruptedFileError(
                f"Rasm faylini ochib bo'lmadi yoki fayl shikastlangan: {file_path.name}",
                details=str(e)
            )

    @classmethod
    def clean_image(
        cls,
        input_path: Path,
        output_path: Path,
        mode: str = "roi_auto",
        roi: Optional[Tuple[int, int, int, int]] = None,
        preset: Optional[str] = None,
        sensitivity: int = 60,
        custom_mask: Optional[np.ndarray] = None,
        method: str = "telea",
        inpaint_radius: int = 4,
        dilate_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Clean watermark/text from an image and save the result.

        Returns:
            Dictionary containing processing metadata (dimensions, mask coverage, output path).
        """
        bgr = cls.load_image(input_path)
        h, w = bgr.shape[:2]

        try:
            # 1. Generate mask using DRY detector
            mask = build_cleaning_mask(
                image_bgr=bgr,
                mode=mode,
                roi=roi,
                preset=preset,
                sensitivity=sensitivity,
                custom_mask=custom_mask
            )

            # 2. Inpaint
            cleaned_bgr = inpaint_frame(
                image_bgr=bgr,
                mask=mask,
                method="telea" if method.lower() == "telea" else "ns",
                inpaint_radius=inpaint_radius,
                dilate_iterations=dilate_iterations
            )

            # 3. Save result
            output_path.parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(output_path), cleaned_bgr)
            if not success:
                raise ProcessingError(f"Natijaviy rasmni saqlab bo'lmadi: {output_path.name}")

            mask_pixels = int(np.count_nonzero(mask))
            coverage_pct = round((mask_pixels / (w * h)) * 100, 2)

            return {
                "width": w,
                "height": h,
                "mask_pixels": mask_pixels,
                "coverage_percent": coverage_pct,
                "output_path": str(output_path),
                "output_name": output_path.name
            }

        except Exception as e:
            if isinstance(e, (CorruptedFileError, ProcessingError)):
                raise
            raise ProcessingError(f"Rasmni tozalash jarayonida xatolik yuz berdi: {str(e)}")
