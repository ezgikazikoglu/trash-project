import torch
import timm
import json
from pathlib import Path

MODEL_DIR  = Path(r"C:\Users\PC\Desktop\egitim_apps\Python\trash-project\model")
META_PATH  = MODEL_DIR / "model_meta.json"
PTH_PATH   = MODEL_DIR / "best_model.pth"
ONNX_PATH  = MODEL_DIR / "model.onnx"

with open(META_PATH) as f:
    meta = json.load(f)

model = timm.create_model(meta["model_name"], pretrained=False, num_classes=meta["num_classes"])
model.load_state_dict(torch.load(PTH_PATH, map_location="cpu"))
model.eval()

dummy = torch.randn(1, 3, meta["img_size"], meta["img_size"])

torch.onnx.export(
    model,
    dummy,
    ONNX_PATH,
    input_names=["image"],
    output_names=["logits"],
    dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
    opset_version=17,
)

print(f"ONNX kaydedildi: {ONNX_PATH}")
print(f"Boyut: {ONNX_PATH.stat().st_size / 1024 / 1024:.1f} MB")
