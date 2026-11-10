"""
Video cleaning processor.
Handles frame-by-frame lightweight inpainting, audio stream preservation,
and progress tracking.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Callable
import subprocess
import os
import cv2
import numpy as np
import imageio_ffmpeg

from .detector import build_cleaning_mask, get_preset_coordinates, create_roi_mask
from .inpainter import inpaint_frame
from .exceptions import CorruptedFileError, ProcessingError


class VideoProcessor:
    """Processes video files to remove watermarks and overlay text."""

    @staticmethod
    def get_ffmpeg_binary() -> str:
        """Return the absolute path of the bundled or system ffmpeg binary."""
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            return "ffmpeg"

    @classmethod
    def extract_first_frame(cls, video_path: Path, output_thumbnail_path: Path) -> Dict[str, Any]:
        """
        Extract the first valid frame of a video as a thumbnail/preview image.
        Also returns video metadata (width, height, fps, total_frames, duration_seconds).
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise CorruptedFileError(f"Videoni ochib bo'lmadi: {video_path.name}")

        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = round(total_frames / fps, 2) if fps > 0 else 0

            ret, frame = cap.read()
            if not ret or frame is None:
                raise CorruptedFileError(f"Video kadrlari o'qilmadi: {video_path.name}")

            output_thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_thumbnail_path), frame)

            return {
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "duration_seconds": duration,
                "thumbnail_path": str(output_thumbnail_path),
                "thumbnail_name": output_thumbnail_path.name
            }
        finally:
            cap.release()

    @classmethod
    def extract_audio(cls, video_path: Path, audio_output_path: Path) -> bool:
        """
        Extract audio stream from source video without re-encoding if present.
        Returns True if audio exists and was extracted, False otherwise.
        """
        ffmpeg_bin = cls.get_ffmpeg_binary()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "copy",
            str(audio_output_path)
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # If copy failed (e.g. incompatible container), try transcode to AAC
            if result.returncode != 0 or not audio_output_path.exists() or audio_output_path.stat().st_size < 100:
                cmd_transcode = [
                    ffmpeg_bin,
                    "-y",
                    "-i", str(video_path),
                    "-vn",
                    "-acodec", "aac",
                    "-b:a", "192k",
                    str(audio_output_path)
                ]
                res2 = subprocess.run(cmd_transcode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res2.returncode != 0 or not audio_output_path.exists() or audio_output_path.stat().st_size < 100:
                    return False
            return True
        except Exception:
            return False

    @classmethod
    def mux_video_and_audio(
        cls,
        clean_video_path: Path,
        audio_path: Path,
        final_output_path: Path
    ) -> bool:
        """
        Mux clean video stream and preserved audio stream into final mp4 file.
        """
        ffmpeg_bin = cls.get_ffmpeg_binary()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", str(clean_video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(final_output_path)
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return res.returncode == 0 and final_output_path.exists() and final_output_path.stat().st_size > 0
        except Exception:
            return False

    @classmethod
    def clean_video(
        cls,
        input_path: Path,
        output_path: Path,
        mode: str = "roi_auto",
        roi: Optional[Tuple[int, int, int, int]] = None,
        preset: Optional[str] = None,
        sensitivity: int = 60,
        custom_mask: Optional[np.ndarray] = None,
        method: str = "telea",
        inpaint_radius: int = 3,
        dilate_iterations: int = 2,
        progress_callback: Optional[Callable[[int, int, float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Clean watermark/symbols from video frames, preserve audio, and save output.

        Args:
            progress_callback: callback(current_frame, total_frames, percent, message)
        """
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise CorruptedFileError(f"Videoni ochib bo'lmadi: {input_path.name}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames <= 0:
            total_frames = 100 # Fallback estimate

        # Temporary files for processing
        temp_dir = output_path.parent / f"tmp_{output_path.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_clean_video = temp_dir / "clean_silent.mp4"
        temp_audio = temp_dir / "extracted_audio.aac"

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(temp_clean_video), fourcc, fps, (width, height))
        if not writer.isOpened():
            # Fallback to alternate fourcc
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            writer = cv2.VideoWriter(str(temp_clean_video), fourcc, fps, (width, height))
            if not writer.isOpened():
                cap.release()
                raise ProcessingError("Video yozish uchun mos codec topilmadi.")

        # Optimize mask calculation for static bounding boxes
        static_mask = None
        if mode in ("roi_box", "preset_box"):
            if mode == "roi_box" and roi is not None:
                static_mask = create_roi_mask((height, width), *roi)
            else:
                rx, ry, rw, rh = get_preset_coordinates(width, height, preset or "bottom_right")
                static_mask = create_roi_mask((height, width), rx, ry, rw, rh)
        elif mode == "custom" and custom_mask is not None:
            if custom_mask.shape[:2] != (height, width):
                static_mask = cv2.resize(custom_mask, (width, height), interpolation=cv2.INTER_NEAREST)
            else:
                static_mask = custom_mask

        current_frame = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                current_frame += 1

                # Generate mask
                if static_mask is not None:
                    mask = static_mask
                else:
                    # Dynamic detection inside ROI or full frame
                    mask = build_cleaning_mask(
                        image_bgr=frame,
                        mode=mode,
                        roi=roi,
                        preset=preset,
                        sensitivity=sensitivity
                    )

                # Inpaint frame
                cleaned_frame = inpaint_frame(
                    image_bgr=frame,
                    mask=mask,
                    method="telea" if method.lower() == "telea" else "ns",
                    inpaint_radius=inpaint_radius,
                    dilate_iterations=dilate_iterations
                )

                writer.write(cleaned_frame)

                if progress_callback and (current_frame % 5 == 0 or current_frame == total_frames):
                    pct = round(min(95.0, (current_frame / total_frames) * 95.0), 1)
                    progress_callback(
                        current_frame,
                        total_frames,
                        pct,
                        f"Kadrlar tozalanmoqda: {current_frame}/{total_frames} ({pct}%)"
                    )

        finally:
            cap.release()
            writer.release()

        # Step 2: Extract audio and mux
        if progress_callback:
            progress_callback(current_frame, total_frames, 96.0, "Ovoz oqimi tekshirilmoqda...")

        has_audio = cls.extract_audio(input_path, temp_audio)

        if has_audio:
            if progress_callback:
                progress_callback(current_frame, total_frames, 98.0, "Video va ovoz birlashtirilmoqda...")

            muxed = cls.mux_video_and_audio(temp_clean_video, temp_audio, output_path)
            if not muxed:
                # Fallback to video without audio if muxing failed
                if temp_clean_video.exists():
                    os.replace(temp_clean_video, output_path)
        else:
            if temp_clean_video.exists():
                os.replace(temp_clean_video, output_path)

        # Cleanup temporary files
        try:
            if temp_audio.exists():
                temp_audio.unlink()
            if temp_clean_video.exists():
                temp_clean_video.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
        except Exception:
            pass

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise ProcessingError("Tozalangan video fayli muvaffaqiyatli saqlanmadi.")

        if progress_callback:
            progress_callback(current_frame, total_frames, 100.0, "Muvaffaqiyatli yakunlandi!")

        return {
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": current_frame,
            "duration_seconds": round(current_frame / fps, 2) if fps > 0 else 0,
            "has_audio": has_audio,
            "output_path": str(output_path),
            "output_name": output_path.name
        }
