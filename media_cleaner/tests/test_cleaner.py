"""
Comprehensive unit and integration tests for MediaCleaner.
Tests synthetic image generation, text detection, inpainting,
and video frame processing.
"""

from pathlib import Path
import unittest
import numpy as np
import cv2

from media_cleaner.core.detector import (
    build_cleaning_mask,
    create_roi_mask,
    get_preset_coordinates,
    detect_text_in_region
)
from media_cleaner.core.inpainter import inpaint_frame, dilate_mask
from media_cleaner.core.image_processor import ImageProcessor
from media_cleaner.core.video_processor import VideoProcessor
from media_cleaner.core.exceptions import CorruptedFileError, CleanerError


class TestMediaCleaner(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "test_data"
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Create a synthetic image with gradient and text watermark
        self.test_img = np.zeros((300, 400, 3), dtype=np.uint8)
        # Add horizontal gradient background
        for i in range(300):
            self.test_img[i, :, 0] = int(120 + 80 * (i / 300)) # B
            self.test_img[i, :, 1] = int(80 + 50 * (i / 300))  # G
            self.test_img[i, :, 2] = int(40 + 30 * (i / 300))  # R

        # Draw clear white text watermark in bottom right
        cv2.putText(
            self.test_img,
            "WATERMARK 2026",
            (210, 275),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        self.sample_img_path = self.test_dir / "sample_watermark.png"
        cv2.imwrite(str(self.sample_img_path), self.test_img)

    def tearDown(self):
        # Clean up test files
        for f in self.test_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            self.test_dir.rmdir()
        except Exception:
            pass

    def test_roi_mask_creation(self):
        """Test ROI mask generation."""
        mask = create_roi_mask((300, 400), x=200, y=250, w=150, h=40)
        self.assertEqual(mask.shape, (300, 400))
        self.assertEqual(mask.dtype, np.uint8)
        self.assertTrue(np.count_nonzero(mask) > 0)
        self.assertEqual(mask[260, 250], 255)
        self.assertEqual(mask[10, 10], 0)

    def test_preset_coordinates(self):
        """Test preset coordinate scaling."""
        x, y, w, h = get_preset_coordinates(1920, 1080, "bottom_right")
        self.assertGreater(x, 1000)
        self.assertGreater(y, 800)
        self.assertGreater(w, 200)
        self.assertGreater(h, 50)

    def test_text_detection_in_patch(self):
        """Test detecting high-contrast text."""
        patch = self.test_img[250:290, 200:390]
        mask = detect_text_in_region(patch, sensitivity=60)
        # Should detect pixels corresponding to text strokes
        self.assertGreater(np.count_nonzero(mask), 50)

    def test_inpainting_telea_and_ns(self):
        """Test inpainting algorithms execution without crashing."""
        mask = create_roi_mask((300, 400), 200, 250, 180, 40)
        
        # Test Telea
        cleaned_telea = inpaint_frame(self.test_img, mask, method="telea", inpaint_radius=3)
        self.assertEqual(cleaned_telea.shape, self.test_img.shape)
        # The white text pixels should be replaced with surrounding background color
        diff = cv2.absdiff(self.test_img, cleaned_telea)
        self.assertGreater(np.sum(diff), 0)

        # Test Navier-Stokes
        cleaned_ns = inpaint_frame(self.test_img, mask, method="ns", inpaint_radius=3)
        self.assertEqual(cleaned_ns.shape, self.test_img.shape)

    def test_image_processor_clean_pipeline(self):
        """Test full ImageProcessor pipeline."""
        output_path = self.test_dir / "cleaned_image.png"
        meta = ImageProcessor.clean_image(
            input_path=self.sample_img_path,
            output_path=output_path,
            mode="roi_box",
            roi=(200, 250, 190, 40),
            method="telea"
        )
        self.assertTrue(output_path.exists())
        self.assertGreater(meta["mask_pixels"], 0)
        self.assertEqual(meta["width"], 400)
        self.assertEqual(meta["height"], 300)

    def test_video_processor_pipeline(self):
        """Test synthetic video creation, thumbnail extraction, and frame cleaning."""
        video_path = self.test_dir / "sample_video.mp4"
        thumb_path = self.test_dir / "sample_thumb.jpg"
        cleaned_video_path = self.test_dir / "cleaned_video.mp4"

        # 1. Create a 15-frame test video
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(video_path), fourcc, 10.0, (400, 300))
        for _ in range(15):
            writer.write(self.test_img)
        writer.release()

        self.assertTrue(video_path.exists())

        # 2. Extract thumbnail
        meta = VideoProcessor.extract_first_frame(video_path, thumb_path)
        self.assertTrue(thumb_path.exists())
        self.assertEqual(meta["width"], 400)
        self.assertEqual(meta["height"], 300)
        self.assertEqual(meta["total_frames"], 15)

        # 3. Clean video
        progress_calls = []
        def on_prog(cur, total, pct, msg):
            progress_calls.append(pct)

        res = VideoProcessor.clean_video(
            input_path=video_path,
            output_path=cleaned_video_path,
            mode="roi_box",
            roi=(200, 250, 190, 40),
            progress_callback=on_prog
        )

        self.assertTrue(cleaned_video_path.exists())
        self.assertEqual(res["total_frames"], 15)
        self.assertGreater(len(progress_calls), 0)


if __name__ == "__main__":
    unittest.main()
