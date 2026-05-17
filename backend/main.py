import json
import sys
import time
import io
from pathlib import Path

import numpy as np
from PIL import Image
import onnxruntime as ort

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── PATHS ────────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    exe_dir = Path(sys.executable).parent
    # Electron paketi: resources/backend/ → model: resources/model/
    packaged = exe_dir.parent / "model"
    # Doğrudan test: dist/server/ → trash-project/model/
    dev      = exe_dir.parent.parent.parent / "model"
    MODEL_DIR = packaged if packaged.exists() else dev
else:
    MODEL_DIR = Path(__file__).parent.parent / "model"
ONNX_PATH  = MODEL_DIR / "model.onnx"
META_PATH  = MODEL_DIR / "model_meta.json"

# ─── MODEL YÜKLEME ────────────────────────────────────────────────────────────
with open(META_PATH, encoding="utf-8") as f:
    meta = json.load(f)

CLASSES  = meta["classes"]
IMG_SIZE = meta["img_size"]

session = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
INPUT_NAME  = session.get_inputs()[0].name
OUTPUT_NAME = session.get_outputs()[0].name

CLASS_LABELS_TR = {
    "cardboard": "Karton",
    "glass":     "Cam",
    "metal":     "Metal",
    "paper":     "Kağıt",
    "plastic":   "Plastik",
    "trash":     "Çöp",
}

print(f"ONNX model yüklendi | Sınıflar: {CLASSES}")

# ─── TRANSFORM (saf numpy/PIL — torch gerektirmez) ────────────────────────────
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

def preprocess(img: Image.Image) -> np.ndarray:
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    arr = np.array(img, dtype=np.float32) / 255.0   # HWC, [0,1]
    arr = (arr - MEAN) / STD                          # normalize
    arr = arr.transpose(2, 0, 1)                      # HWC → CHW
    return arr[np.newaxis, :, :, :]                   # batch dim

def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()

# ─── APP ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Atık Sınıflandırıcı API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── SCHEMAS ──────────────────────────────────────────────────────────────────
class PredictionResult(BaseModel):
    class_name: str
    class_name_tr: str
    confidence: float
    probabilities: dict[str, float]
    inference_ms: float

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "classes": CLASSES}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResult)
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Sadece görsel dosyası yükleyin.")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 10MB'ı geçemez.")

    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Görsel okunamadı.")

    inp = preprocess(img)

    t0 = time.perf_counter()
    logits = session.run([OUTPUT_NAME], {INPUT_NAME: inp})[0][0]
    inference_ms = (time.perf_counter() - t0) * 1000

    probs    = softmax(logits)
    pred_idx = int(probs.argmax())
    class_name = CLASSES[pred_idx]

    return PredictionResult(
        class_name    = class_name,
        class_name_tr = CLASS_LABELS_TR[class_name],
        confidence    = float(probs[pred_idx]),
        probabilities = {CLASSES[i]: round(float(p), 4) for i, p in enumerate(probs)},
        inference_ms  = round(inference_ms, 2),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
