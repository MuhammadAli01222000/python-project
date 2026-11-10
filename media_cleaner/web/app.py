"""
FastAPI application for Media Cleaner.
Provides REST API endpoints for upload, asynchronous cleaning,
real-time status polling, and file download.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import uuid
import shutil
import concurrent.futures

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import (
    UPLOAD_DIR,
    OUTPUT_DIR,
    STATIC_DIR,
    TEMPLATES_DIR,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    ALL_ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES
)
from ..core.exceptions import CleanerError, UnsupportedFormatError, CorruptedFileError, ProcessingError
from ..core.image_processor import ImageProcessor
from ..core.video_processor import VideoProcessor

app = FastAPI(title="Media Watermark & Text Cleaner", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Background thread pool executor for heavy CPU processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

# In-memory task tracker
tasks: Dict[str, Dict[str, Any]] = {}
uploads_meta: Dict[str, Dict[str, Any]] = {}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler to avoid bare 500 pages."""
    error_msg = f"Server xatoligi: {str(exc)}"
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse(
            content=f"""
            <div style="font-family: sans-serif; padding: 40px; background: #0f172a; color: #f8fafc; min-height: 100vh;">
                <h2 style="color: #ef4444;">Serverda kutilmagan xatolik yuz berdi</h2>
                <p style="color: #94a3b8; font-family: monospace; background: #1e293b; padding: 16px; border-radius: 8px;">
                    {error_msg}
                </p>
                <a href="/" style="color: #818cf8; text-decoration: underline;">Bosh sahifaga qaytish</a>
            </div>
            """,
            status_code=500
        )
    return JSONResponse(status_code=500, content={"detail": error_msg})


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Render main web UI."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/upload")
async def upload_media(file: UploadFile = File(...)):
    """
    Handle media file upload, validate format, and extract preview metadata.
    """
    filename = file.filename or "uploaded_media"
    ext = Path(filename).suffix.lower()

    if ext not in ALL_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Qo'llab-quvvatlanmaydigan fayl formati: '{ext}'. Faqat rasm (JPG, PNG, WEBP...) yoki video (MP4, AVI, MKV, MOV...) yuklang."
        )

    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}{ext}"
    saved_path = UPLOAD_DIR / stored_filename

    # Save uploaded file safely
    try:
        with saved_path.open("wb") as buffer:
            total_read = 0
            while chunk := await file.read(1024 * 1024):
                total_read += len(chunk)
                if total_read > MAX_UPLOAD_SIZE_BYTES:
                    saved_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Fayl hajmi ruxsat etilgan me'yordan oshib ketdi (maksimal: {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB)."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Faylni saqlashda xatolik: {str(e)}")

    # Detect media type and generate preview
    is_video = ext in VIDEO_EXTENSIONS
    media_type = "video" if is_video else "image"

    try:
        if is_video:
            thumb_filename = f"{file_id}_thumb.jpg"
            thumb_path = UPLOAD_DIR / thumb_filename
            meta = VideoProcessor.extract_first_frame(saved_path, thumb_path)
            preview_url = f"/api/media/upload/{thumb_filename}"
        else:
            bgr = ImageProcessor.load_image(saved_path)
            h, w = bgr.shape[:2]
            meta = {
                "width": w,
                "height": h,
                "duration_seconds": 0,
                "fps": 0,
                "total_frames": 1
            }
            preview_url = f"/api/media/upload/{stored_filename}"

        meta_info = {
            "file_id": file_id,
            "original_name": filename,
            "stored_filename": stored_filename,
            "media_type": media_type,
            "extension": ext,
            "file_size": saved_path.stat().st_size,
            "preview_url": preview_url,
            **meta
        }
        uploads_meta[file_id] = meta_info
        return JSONResponse(content={"success": True, "meta": meta_info})

    except CleanerError as ce:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=ce.message)
    except Exception as e:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Faylni tahlil qilishda xatolik: {str(e)}")


def _run_cleaning_job(
    task_id: str,
    file_id: str,
    mode: str,
    roi: Optional[tuple],
    preset: Optional[str],
    sensitivity: int,
    method: str,
    inpaint_radius: int,
    dilate_iterations: int
):
    """Background worker for CPU-bound image/video inpainting."""
    meta = uploads_meta.get(file_id)
    if not meta:
        tasks[task_id] = {
            "status": "failed",
            "progress": 0,
            "error": "Fayl ma'lumotlari topilmadi. Qaytadan yuklang."
        }
        return

    input_path = UPLOAD_DIR / meta["stored_filename"]
    is_video = meta["media_type"] == "video"

    ext = meta["extension"]
    output_filename = f"cleaned_{file_id}{ext}"
    output_path = OUTPUT_DIR / output_filename

    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["message"] = "Tozalash boshlandi..."

        if is_video:
            def on_progress(cur, total, pct, msg):
                tasks[task_id]["progress"] = pct
                tasks[task_id]["message"] = msg

            res = VideoProcessor.clean_video(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                roi=roi,
                preset=preset,
                sensitivity=sensitivity,
                method=method,
                inpaint_radius=inpaint_radius,
                dilate_iterations=dilate_iterations,
                progress_callback=on_progress
            )
        else:
            tasks[task_id]["progress"] = 30.0
            tasks[task_id]["message"] = "Rasm tahlil qilinmoqda va tozalanmoqda..."
            res = ImageProcessor.clean_image(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                roi=roi,
                preset=preset,
                sensitivity=sensitivity,
                method=method,
                inpaint_radius=inpaint_radius,
                dilate_iterations=dilate_iterations
            )
            tasks[task_id]["progress"] = 100.0

        tasks[task_id] = {
            "status": "completed",
            "progress": 100.0,
            "message": "Muvaffaqiyatli yakunlandi!",
            "result": {
                "download_url": f"/api/download/{task_id}",
                "preview_url": f"/api/media/output/{output_filename}",
                "output_filename": output_filename,
                "media_type": meta["media_type"],
                "file_size": output_path.stat().st_size,
                **res
            }
        }

    except CleanerError as ce:
        tasks[task_id] = {
            "status": "failed",
            "progress": 0,
            "error": ce.message
        }
    except Exception as e:
        tasks[task_id] = {
            "status": "failed",
            "progress": 0,
            "error": f"Jarayonda kutilmagan xatolik yuz berdi: {str(e)}"
        }


@app.post("/api/process")
async def start_processing(
    file_id: str = Form(...),
    mode: str = Form("roi_box"),
    roi_x: Optional[int] = Form(None),
    roi_y: Optional[int] = Form(None),
    roi_w: Optional[int] = Form(None),
    roi_h: Optional[int] = Form(None),
    preset: Optional[str] = Form("bottom_right"),
    sensitivity: int = Form(60),
    method: str = Form("telea"),
    inpaint_radius: int = Form(3),
    dilate_iterations: int = Form(2)
):
    """Initiate an asynchronous cleaning task."""
    if file_id not in uploads_meta:
        raise HTTPException(status_code=404, detail="Yuklangan fayl topilmadi. Avval fayl yuklang.")

    roi = None
    if roi_x is not None and roi_y is not None and roi_w is not None and roi_h is not None:
        roi = (roi_x, roi_y, roi_w, roi_h)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "progress": 0.0,
        "message": "Vazifa navbatga qo'yildi...",
        "task_id": task_id
    }

    executor.submit(
        _run_cleaning_job,
        task_id=task_id,
        file_id=file_id,
        mode=mode,
        roi=roi,
        preset=preset,
        sensitivity=sensitivity,
        method=method,
        inpaint_radius=inpaint_radius,
        dilate_iterations=dilate_iterations
    )

    return JSONResponse(content={"success": True, "task_id": task_id})


@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """Poll processing task progress and results."""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi.")
    return JSONResponse(content=task)


@app.get("/api/download/{task_id}")
async def download_cleaned_file(task_id: str):
    """Download cleaned media file."""
    task = tasks.get(task_id)
    if not task or task.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Fayl hali tayyor emas yoki xatolik yuz bergan.")

    result = task.get("result", {})
    output_filename = result.get("output_filename")
    if not output_filename:
        raise HTTPException(status_code=404, detail="Natijaviy fayl nomi topilmadi.")

    file_path = OUTPUT_DIR / output_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fayl diskda topilmadi.")

    return FileResponse(
        path=str(file_path),
        filename=output_filename,
        media_type="application/octet-stream"
    )


@app.get("/api/media/{folder}/{filename}")
async def serve_media(folder: str, filename: str):
    """Serve uploaded or processed media file."""
    target_dir = UPLOAD_DIR if folder == "upload" else OUTPUT_DIR
    file_path = target_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fayl topilmadi.")
    return FileResponse(path=str(file_path))
