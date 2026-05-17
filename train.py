import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from sklearn.model_selection import train_test_split

import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import Image

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DATA_DIR   = Path(r"C:\Users\PC\Desktop\egitim_apps\Python\trash-project\data\dataset-resized")
SAVE_DIR   = Path(r"C:\Users\PC\Desktop\egitim_apps\Python\trash-project\model")
IMG_SIZE   = 224
BATCH_SIZE = 16
EPOCHS     = 30
LR         = 1e-4
SEED       = 42

SAVE_DIR.mkdir(parents=True, exist_ok=True)
torch.manual_seed(SEED)
np.random.seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {DEVICE}")
if DEVICE.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")


# ─── ALBUMENTATIONS WRAPPER ───────────────────────────────────────────────────
class AlbumentationsDataset(torch.utils.data.Dataset):
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        img, label = self.subset[idx]
        img = np.array(img)  # PIL → numpy
        if self.transform:
            img = self.transform(image=img)["image"]
        return img, label


# ─── TRANSFORMS ───────────────────────────────────────────────────────────────
train_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.2),
    A.RandomRotate90(p=0.3),
    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
    A.GaussNoise(p=0.2),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])

val_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])


# ─── DATASET & SPLIT ──────────────────────────────────────────────────────────
raw_dataset = datasets.ImageFolder(DATA_DIR)
classes = raw_dataset.classes
num_classes = len(classes)
print(f"\nSınıflar: {classes}")

labels = [label for _, label in raw_dataset.samples]
label_counts = Counter(labels)
print("Sınıf dağılımı:", {classes[k]: v for k, v in sorted(label_counts.items())})

all_idx = list(range(len(raw_dataset)))
train_idx, temp_idx = train_test_split(all_idx, test_size=0.30, stratify=labels, random_state=SEED)
temp_labels = [labels[i] for i in temp_idx]
val_idx, test_idx = train_test_split(temp_idx, test_size=0.50, stratify=temp_labels, random_state=SEED)

print(f"\nTrain: {len(train_idx)} | Val: {len(val_idx)} | Test: {len(test_idx)}")

train_ds = AlbumentationsDataset(Subset(raw_dataset, train_idx), transform=train_transform)
val_ds   = AlbumentationsDataset(Subset(raw_dataset, val_idx),   transform=val_transform)
test_ds  = AlbumentationsDataset(Subset(raw_dataset, test_idx),  transform=val_transform)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=0)


# ─── CLASS WEIGHTS (dengesizlik için) ─────────────────────────────────────────
train_labels = [labels[i] for i in train_idx]
counts = np.array([train_labels.count(i) for i in range(num_classes)], dtype=np.float32)
class_weights = torch.tensor(counts.sum() / (num_classes * counts)).to(DEVICE)
print(f"\nSınıf ağırlıkları: { {classes[i]: round(class_weights[i].item(), 3) for i in range(num_classes)} }")


# ─── MODEL ────────────────────────────────────────────────────────────────────
model = timm.create_model("efficientnetv2_rw_s.ra2_in1k", pretrained=True, num_classes=num_classes)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss(weight=class_weights)
optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)


# ─── EĞİTİM DÖNGÜSÜ ──────────────────────────────────────────────────────────
history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
best_val_acc = 0.0

def run_epoch(loader, training=True):
    model.train() if training else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    ctx = torch.enable_grad() if training else torch.no_grad()
    with ctx:
        for imgs, lbls in loader:
            imgs, lbls = imgs.to(DEVICE), lbls.to(DEVICE)
            if training:
                optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            if training:
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            correct += (out.argmax(1) == lbls).sum().item()
            total += imgs.size(0)
    return total_loss / total, correct / total


print("\n" + "="*60)
print("EĞİTİM BAŞLIYOR")
print("="*60)

for epoch in range(1, EPOCHS + 1):
    t0 = time.time()
    train_loss, train_acc = run_epoch(train_loader, training=True)
    val_loss,   val_acc   = run_epoch(val_loader,   training=False)
    scheduler.step()

    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_loss)
    history["train_acc"].append(train_acc)
    history["val_acc"].append(val_acc)

    elapsed = time.time() - t0
    print(f"Epoch [{epoch:02d}/{EPOCHS}] "
          f"T.Loss: {train_loss:.4f} T.Acc: {train_acc:.4f} | "
          f"V.Loss: {val_loss:.4f} V.Acc: {val_acc:.4f} | "
          f"{elapsed:.1f}s")

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), SAVE_DIR / "best_model.pth")
        print(f"  ✓ En iyi model kaydedildi (val_acc={val_acc:.4f})")


# ─── TEST DEĞERLENDİRME ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("TEST SETİ DEĞERLENDİRMESİ")
print("="*60)
model.load_state_dict(torch.load(SAVE_DIR / "best_model.pth"))
test_loss, test_acc = run_epoch(test_loader, training=False)
print(f"Test Loss: {test_loss:.4f} | Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")


# ─── CONFUSION MATRIX ─────────────────────────────────────────────────────────
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

all_preds, all_targets = [], []
model.eval()
with torch.no_grad():
    for imgs, lbls in test_loader:
        imgs = imgs.to(DEVICE)
        preds = model(imgs).argmax(1).cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(lbls.numpy())

print("\nClassification Report:")
print(classification_report(all_targets, all_preds, target_names=classes))

cm = confusion_matrix(all_targets, all_preds)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes, ax=ax)
ax.set_xlabel("Tahmin"); ax.set_ylabel("Gerçek"); ax.set_title("Confusion Matrix")
plt.tight_layout()
plt.savefig(SAVE_DIR / "confusion_matrix.png", dpi=150)
plt.close()


# ─── EĞİTİM GRAFİKLERİ ───────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.plot(history["train_loss"], label="Train Loss")
ax1.plot(history["val_loss"],   label="Val Loss")
ax1.set_title("Loss"); ax1.set_xlabel("Epoch"); ax1.legend(); ax1.grid(True)

ax2.plot(history["train_acc"], label="Train Acc")
ax2.plot(history["val_acc"],   label="Val Acc")
ax2.set_title("Accuracy"); ax2.set_xlabel("Epoch"); ax2.legend(); ax2.grid(True)

plt.tight_layout()
plt.savefig(SAVE_DIR / "training_curves.png", dpi=150)
plt.close()

print(f"\nGrafikler kaydedildi: {SAVE_DIR}")


# ─── MODEL BİLGİLERİNİ KAYDET ─────────────────────────────────────────────────
meta = {
    "classes": classes,
    "num_classes": num_classes,
    "img_size": IMG_SIZE,
    "model_name": "efficientnetv2_rw_s.ra2_in1k",
    "best_val_acc": best_val_acc,
    "test_acc": test_acc,
}
with open(SAVE_DIR / "model_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)

print(f"\nEn iyi Val Accuracy : {best_val_acc*100:.2f}%")
print(f"Test Accuracy       : {test_acc*100:.2f}%")
print("Eğitim tamamlandı!")
