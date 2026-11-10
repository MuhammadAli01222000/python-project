/**
 * MediaCleaner Frontend Controller
 * Handles interactive ROI canvas, presets, async file upload,
 * progress polling, and error handling.
 */

// Application State
const state = {
    file: null,
    meta: null,
    previewImg: new Image(),
    scaleFactor: 1.0,
    roi: null, // {x, y, w, h} in original media pixels
    activePreset: "bottom_right",
    isDrawing: false,
    startX: 0,
    startY: 0,
    pollingInterval: null
};

// DOM References
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const canvasContainer = document.getElementById("canvas-container");
const canvas = document.getElementById("interactive-canvas");
const ctx = canvas.getContext("2d");
const roiCoordsDisplay = document.getElementById("roi-coords-display");
const fileInfoBadge = document.getElementById("file-info-badge");
const btnSubmit = document.getElementById("btn-submit");
const errorBanner = document.getElementById("error-banner");
const errorMessage = document.getElementById("error-message");
const progressPanel = document.getElementById("progress-panel");
const progressPercent = document.getElementById("progress-percent");
const progressBarFill = document.getElementById("progress-bar-fill");
const progressDetails = document.getElementById("progress-details");
const resultPanel = document.getElementById("result-panel");
const resultMediaContainer = document.getElementById("result-media-container");
const btnDownload = document.getElementById("btn-download");

// Preset definitions (percentages)
const PRESETS = {
    bottom_right: { rx: 0.70, ry: 0.85, rw: 0.28, rh: 0.13 },
    top_right: { rx: 0.70, ry: 0.02, rw: 0.28, rh: 0.13 },
    bottom_left: { rx: 0.02, ry: 0.85, rw: 0.28, rh: 0.13 },
    top_left: { rx: 0.02, ry: 0.02, rw: 0.28, rh: 0.13 },
    bottom_subtitles: { rx: 0.05, ry: 0.82, rw: 0.90, rh: 0.16 }
};

// --- Error Handling ---
function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.style.display = "flex";
    errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function dismissError() {
    errorBanner.style.display = "none";
}

// --- Drag & Drop & Upload ---
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
});

dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("drag-over");
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

async function handleFileSelection(file) {
    dismissError();
    state.file = file;

    // Show loading state
    dropzone.style.opacity = "0.5";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Faylni yuklashda xatolik yuz berdi.");
        }

        state.meta = data.meta;
        initMediaWorkspace();
    } catch (err) {
        showError(err.message);
        dropzone.style.opacity = "1";
    }
}

// --- Workspace Initialization ---
function initMediaWorkspace() {
    dropzone.style.display = "none";
    canvasContainer.style.display = "flex";
    btnSubmit.disabled = false;

    // Display metadata badge
    const isVideo = state.meta.media_type === "video";
    const durationText = isVideo ? ` | ${state.meta.duration_seconds}s (${state.meta.total_frames} kadr)` : "";
    fileInfoBadge.textContent = `${state.meta.original_name} (${state.meta.width}x${state.meta.height}${durationText})`;
    fileInfoBadge.style.display = "inline-block";

    // Load preview into canvas
    state.previewImg.onload = () => {
        setupCanvasDimensions();
        // Default to active preset
        applyPreset(state.activePreset);
    };
    state.previewImg.src = state.meta.preview_url;
}

function setupCanvasDimensions() {
    const naturalWidth = state.meta.width;
    const naturalHeight = state.meta.height;

    // Constrain display dimensions inside container
    const maxDisplayWidth = canvasContainer.clientWidth || 700;
    const maxDisplayHeight = 480;

    const ratio = Math.min(maxDisplayWidth / naturalWidth, maxDisplayHeight / naturalHeight, 1.0);
    const displayW = Math.round(naturalWidth * ratio);
    const displayH = Math.round(naturalHeight * ratio);

    canvas.width = displayW;
    canvas.height = displayH;
    state.scaleFactor = naturalWidth / displayW;

    drawCanvas();
}

window.addEventListener("resize", () => {
    if (state.meta && state.previewImg.complete) {
        setupCanvasDimensions();
    }
});

// --- Canvas Rendering & Drawing ---
function drawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Draw background media frame
    ctx.drawImage(state.previewImg, 0, 0, canvas.width, canvas.height);

    // Draw ROI if selected
    if (state.roi) {
        const rx = state.roi.x / state.scaleFactor;
        const ry = state.roi.y / state.scaleFactor;
        const rw = state.roi.w / state.scaleFactor;
        const rh = state.roi.h / state.scaleFactor;

        // Semi-transparent overlay box
        ctx.fillStyle = "rgba(99, 102, 241, 0.28)";
        ctx.fillRect(rx, ry, rw, rh);

        // Border
        ctx.strokeStyle = "#818cf8";
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 4]);
        ctx.strokeRect(rx, ry, rw, rh);
        ctx.setLineDash([]);

        // Corner handles
        ctx.fillStyle = "#ffffff";
        const handleSize = 6;
        ctx.fillRect(rx - handleSize / 2, ry - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(rx + rw - handleSize / 2, ry - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(rx - handleSize / 2, ry + rh - handleSize / 2, handleSize, handleSize);
        ctx.fillRect(rx + rw - handleSize / 2, ry + rh - handleSize / 2, handleSize, handleSize);

        // Update display text
        roiCoordsDisplay.innerHTML = `Tanlangan soha: <span class="highlight">[x:${Math.round(state.roi.x)}, y:${Math.round(state.roi.y)}, w:${Math.round(state.roi.w)}, h:${Math.round(state.roi.h)}]</span>`;
    } else {
        roiCoordsDisplay.innerHTML = `Tanlangan soha: <span class="highlight">Butun kadr</span>`;
    }
}

// --- Interactive Mouse ROI Selection ---
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    state.isDrawing = true;
    state.startX = e.clientX - rect.left;
    state.startY = e.clientY - rect.top;

    // Reset active preset buttons when user draws custom box
    document.querySelectorAll(".btn-preset").forEach(btn => btn.classList.remove("active"));
    state.activePreset = null;
});

canvas.addEventListener("mousemove", (e) => {
    if (!state.isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    const x = Math.min(state.startX, currentX);
    const y = Math.min(state.startY, currentY);
    const w = Math.abs(currentX - state.startX);
    const h = Math.abs(currentY - state.startY);

    // Convert to original media pixel space
    state.roi = {
        x: Math.round(x * state.scaleFactor),
        y: Math.round(y * state.scaleFactor),
        w: Math.round(w * state.scaleFactor),
        h: Math.round(h * state.scaleFactor)
    };

    drawCanvas();
});

canvas.addEventListener("mouseup", () => {
    state.isDrawing = false;
    // Discard tiny accidental clicks
    if (state.roi && (state.roi.w < 10 || state.roi.h < 10)) {
        state.roi = null;
        drawCanvas();
    }
});

// --- Presets ---
function applyPreset(presetKey) {
    if (!state.meta || !PRESETS[presetKey]) return;

    state.activePreset = presetKey;
    const p = PRESETS[presetKey];

    state.roi = {
        x: Math.round(p.rx * state.meta.width),
        y: Math.round(p.ry * state.meta.height),
        w: Math.round(p.rw * state.meta.width),
        h: Math.round(p.rh * state.meta.height)
    };

    document.querySelectorAll(".btn-preset").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.preset === presetKey);
    });

    drawCanvas();
}

function resetROI() {
    state.roi = null;
    state.activePreset = null;
    document.querySelectorAll(".btn-preset").forEach(btn => btn.classList.remove("active"));
    drawCanvas();
}

function updateModeUI() {
    const mode = document.getElementById("clean-mode").value;
    if (mode === "full_auto") {
        resetROI();
    }
}

// --- Processing Execution & Polling ---
async function handleStartClean(e) {
    e.preventDefault();
    if (!state.meta) return;

    dismissError();
    resultPanel.style.display = "none";
    progressPanel.style.display = "flex";
    btnSubmit.disabled = true;

    progressBarFill.style.width = "0%";
    progressPercent.textContent = "0%";
    progressDetails.textContent = "So'rov serverga yuborilmoqda...";

    const mode = document.getElementById("clean-mode").value;
    const method = document.getElementById("inpaint-method").value;
    const inpaintRadius = document.getElementById("inpaint-radius").value;
    const dilateIterations = document.getElementById("dilate-iterations").value;

    const formData = new FormData();
    formData.append("file_id", state.meta.file_id);
    formData.append("mode", mode);
    formData.append("method", method);
    formData.append("inpaint_radius", inpaintRadius);
    formData.append("dilate_iterations", dilateIterations);

    if (state.roi) {
        formData.append("roi_x", state.roi.x);
        formData.append("roi_y", state.roi.y);
        formData.append("roi_w", state.roi.w);
        formData.append("roi_h", state.roi.h);
    }
    if (state.activePreset) {
        formData.append("preset", state.activePreset);
    }

    try {
        const response = await fetch("/api/process", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Tozalash vazifasini boshlashda xatolik.");
        }

        pollStatus(data.task_id);
    } catch (err) {
        showError(err.message);
        progressPanel.style.display = "none";
        btnSubmit.disabled = false;
    }
}

function pollStatus(taskId) {
    if (state.pollingInterval) clearInterval(state.pollingInterval);

    state.pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${taskId}`);
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "Holatni tekshirib bo'lmadi.");
            }

            const pct = Math.round(data.progress || 0);
            progressBarFill.style.width = `${pct}%`;
            progressPercent.textContent = `${pct}%`;
            progressDetails.textContent = data.message || "Ishlanmoqda...";

            if (data.status === "completed") {
                clearInterval(state.pollingInterval);
                finishTask(data.result);
            } else if (data.status === "failed") {
                clearInterval(state.pollingInterval);
                throw new Error(data.error || "Jarayonda xatolik yuz berdi.");
            }
        } catch (err) {
            clearInterval(state.pollingInterval);
            showError(err.message);
            progressPanel.style.display = "none";
            btnSubmit.disabled = false;
        }
    }, 700);
}

function finishTask(result) {
    progressPanel.style.display = "none";
    resultPanel.style.display = "flex";
    btnSubmit.disabled = false;

    // Render result preview
    resultMediaContainer.innerHTML = "";
    if (result.media_type === "video") {
        const video = document.createElement("video");
        video.src = result.preview_url;
        video.controls = true;
        video.autoplay = false;
        resultMediaContainer.appendChild(video);
    } else {
        const img = document.createElement("img");
        img.src = result.preview_url;
        img.alt = "Cleaned Result";
        resultMediaContainer.appendChild(img);
    }

    btnDownload.href = result.download_url;
    resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function resetAll() {
    dismissError();
    state.file = null;
    state.meta = null;
    state.roi = null;
    state.activePreset = "bottom_right";

    if (state.pollingInterval) clearInterval(state.pollingInterval);

    fileInput.value = "";
    dropzone.style.display = "flex";
    dropzone.style.opacity = "1";
    canvasContainer.style.display = "none";
    fileInfoBadge.style.display = "none";
    progressPanel.style.display = "none";
    resultPanel.style.display = "none";
    btnSubmit.disabled = true;
}
