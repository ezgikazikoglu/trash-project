# ♻️ Atık Sınıflandırıcı

Görsel tabanlı çevresel atık sınıflandırma uygulaması. Derin öğrenme modeli ile yüklenen görseldeki atığın türünü otomatik olarak tespit eder.

## Demo

![Uygulama Ekran Görüntüsü](docs/demo.png)

## Özellikler

- 6 atık kategorisini sınıflandırır: **Karton, Cam, Metal, Kağıt, Plastik, Çöp**
- **%94.47** test doğruluğu
- Görsel sürükle & bırak desteği
- Her sınıf için güven yüzdesi ve olasılık dağılımı
- Web arayüzü (React) ve masaüstü uygulaması (Electron)

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Model | EfficientNetV2-RW-S (PyTorch ile eğitildi) |
| Inference | ONNX Runtime (CPU) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + Vite + Tailwind CSS |
| Masaüstü | Electron |
| Paketleme | PyInstaller + electron-builder |

## Kurulum

### Gereksinimler

- Python 3.10+
- Node.js 18+
- Git LFS (model dosyası için)

### 1. Repoyu klonla

```bash
git clone https://github.com/ezgikazikoglu/trash-project.git
cd trash-project
```

> Git LFS kurulu değilse: `git lfs install && git lfs pull`

### 2. Backend

```bash
pip install fastapi uvicorn onnxruntime pillow numpy python-multipart
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend (Web)

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda `http://localhost:5173` adresini aç.

## Model Eğitimi

Modeli sıfırdan eğitmek için:

```bash
pip install torch torchvision timm albumentations scikit-learn seaborn
```

Veri setini [Kaggle'dan](https://www.kaggle.com/datasets/feyzazkefe/trashnet) indirip `data/dataset-resized/` klasörüne çıkart, ardından:

```bash
python train.py
```

Eğitim sonunda `model/best_model.pth` oluşur. ONNX'e dönüştürmek için:

```bash
python export_onnx.py
```

## Masaüstü Uygulaması (Electron)

### Gereksinimler
- Windows Developer Mode açık olmalı (Ayarlar → Gizlilik ve Güvenlik → Geliştiriciler)

### Build

```bash
# 1. Backend exe
cd backend
python -m PyInstaller server.spec --distpath dist --workpath build --noconfirm

# 2. Electron uygulaması
cd ../frontend
npx electron-builder
```

Çıktı: `frontend/release/win-unpacked/Atık Sınıflandırıcı.exe`

## Veri Seti

[TrashNet](https://www.kaggle.com/datasets/feyzazkefe/trashnet) — 6 sınıf, ~2.527 görsel

| Sınıf | Görsel Sayısı |
|---|---|
| Kağıt | 594 |
| Cam | 501 |
| Plastik | 482 |
| Metal | 410 |
| Karton | 403 |
| Çöp | 137 |

## Model Performansı

| Metrik | Değer |
|---|---|
| Test Accuracy | **%94.47** |
| Val Accuracy | %95.25 |
| Model | EfficientNetV2-RW-S |
| Epoch | 30 |
| Batch Size | 16 |

### Sınıf Bazında F1 Skoru

| Sınıf | F1 |
|---|---|
| Cam | 0.97 |
| Kağıt | 0.96 |
| Çöp | 0.95 |
| Karton | 0.94 |
| Plastik | 0.92 |
| Metal | 0.92 |

## Proje Yapısı

```
trash-project/
├── train.py                 # Model eğitimi
├── export_onnx.py           # ONNX dönüştürme
├── backend/
│   ├── main.py              # FastAPI uygulaması
│   ├── server.spec          # PyInstaller yapılandırması
│   └── requirements.txt
├── frontend/
│   ├── electron/
│   │   └── main.js          # Electron ana süreç
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── UploadZone.jsx
│   │       └── ResultCard.jsx
│   ├── package.json
│   └── vite.config.js
└── model/
    ├── model.onnx           # Eğitilmiş model (Git LFS)
    └── model_meta.json      # Sınıf bilgileri
```

## API

Backend `http://localhost:8000` üzerinde çalışır.

| Endpoint | Method | Açıklama |
|---|---|---|
| `/` | GET | Durum bilgisi |
| `/health` | GET | Sağlık kontrolü |
| `/predict` | POST | Görsel → tahmin |

### `/predict` Yanıt Örneği

```json
{
  "class_name": "plastic",
  "class_name_tr": "Plastik",
  "confidence": 0.9921,
  "probabilities": {
    "cardboard": 0.0001,
    "glass": 0.0012,
    "metal": 0.0048,
    "paper": 0.0003,
    "plastic": 0.9921,
    "trash": 0.0015
  },
  "inference_ms": 18.4
}
```

## Lisans

MIT
