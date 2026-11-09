# Smart Event Ticketing System — Face Recognition Using HOG, KNN & PSO

A full-stack, research-grade event ticketing platform integrating **two-stage access authentication**: cryptographically secure digital QR tokens and facial identity verification utilizing **Histogram of Oriented Gradients (HOG)**, **K-Nearest Neighbors (KNN)**, and **Particle Swarm Optimization (PSO)**.

---

## 1. Academic Reference

This system is developed based on the empirical computer vision and machine learning methodology presented in:

> **"Attendance System with Face Recognition Using K-Nearest Neighbor, Particle Swarm Optimization, and Histogram of Oriented Gradients."**  
> Mardi Hardjianto, Agnes Aryasanti, Putri Hayati.  
> *Journal of Embedded System Security and Intelligent Systems (JESSI)*, Vol. 7, No. 4, 2026, pp. 50–66.  
> Reference document located at: [`docs/references/View of Attendance System with Face Recognition Using K-Nearest Neighbor, Particle Swarm Optimization, and Histogram of Oriented Gradients.pdf`](docs/references/)

### Key Methodological Parameters
* **Facial Normalization:** 128 × 128 pixels grayscale conversion using standard NTSC/BT.601 weights ($Gray = 0.2989R + 0.5870G + 0.1140B$).
* **HOG Descriptor:** 1D derivative filters ($[-1, 0, 1]$ and $[-1, 0, 1]^T$), 9 gradient orientation bins, $8 \times 8$ pixel cells, $2 \times 2$ cell blocks with L2-Hys normalization $\rightarrow$ **8,100 numerical values**.
* **Classification Metric:** Euclidean distance $d(x, y) = \sqrt{\sum (x_i - y_i)^2}$.
* **PSO Hyperparameter Search:** Swarm velocity & position updates tuning the neighborhood parameter $k$ and rejection threshold $\tau$ while penalizing False Acceptance Rate (FAR).
* **Single-Use Enforcement:** Atomic conditional database update transitioning tickets from `ACTIVE` to `USED`.

---

## 2. Technology Stack

* **Frontend:** Native HTML5, CSS3 Custom Properties (Design System), Vanilla JavaScript ES6+, Jinja2 server-side rendering, MediaDevices & Canvas APIs. (Zero React/Node.js runtime overhead).
* **Backend:** Python 3.10+ / 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.0.
* **Database:** MySQL 8.0 (Laragon default with PyMySQL driver) / SQLite zero-config development fallback.
* **Computer Vision & ML:** OpenCV, scikit-image, scikit-learn, NumPy, Matplotlib.
* **Security:** Argon2id password hashing, signed session cookies, SHA-256 token hashing.

---

## 3. System Architecture & Two-Stage Verification

```mermaid
sequenceDiagram
    autonumber
    actor Participant
    actor Operator
    participant Scanner as Turnstile Scanner
    participant Backend as FastAPI Backend
    participant DB as Database & Gallery

    Note over Participant,DB: Stage 1: QR Ticket Validation
    Participant->>Operator: Presents QR Ticket
    Operator->>Scanner: Scans QR Code
    Scanner->>Backend: POST /api/checkin/validate-qr (token)
    Backend->>DB: Query token hash & verify status == ACTIVE
    Backend-->>Scanner: Valid ticket -> Returns 3-min Verification Session

    Note over Participant,DB: Stage 2: Biometric Facial Verification
    Participant->>Scanner: Faces live camera
    Operator->>Scanner: Clicks "Verify Face"
    Scanner->>Backend: POST /api/checkin/verify-face (session_id, frame)
    Backend->>Backend: OpenCV Detection -> 128x128 Resize -> HOG (8,100 dims)
    Backend->>DB: Query enrolled samples for ticket owner
    Backend->>Backend: KNN Euclidean Distance & PSO Threshold Check
    alt Face Matches Owner & Distance <= Threshold
        Backend->>DB: ATOMIC UPDATE tickets SET status='USED', used_at=now
        Backend-->>Scanner: ACCESS GRANTED (Welcome!)
    else Mismatch or Exceeds Threshold
        Backend->>DB: Log Failed Attempt (Ticket remains ACTIVE)
        Backend-->>Scanner: ACCESS DENIED (Mismatch / Exceeded Threshold)
    end
```

---

## 4. Cara Menjalankan Aplikasi (Quickstart)

### Cara Cepat (Menggunakan PowerShell Shortcut Runner)

Di terminal PowerShell, Anda cukup menggunakan script `run.ps1`:

```powershell
# 1. Menjalankan server web lokal (FastAPI + Uvicorn)
.\run.ps1 server

# 2. Menjalankan seluruh automated unit test (12 passed)
.\run.ps1 test

# 3. Menjalankan eksperimen riset benchmark (HOG-KNN vs PSO-KNN)
.\run.ps1 experiment

# 4. Menjalankan migrasi skema database (Alembic)
.\run.ps1 migrate
```

Buka browser Anda di: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### Cara Alternatif (Manual via Virtual Environment)

Jika ingin menjalankan perintah langsung tanpa runner:

```powershell
# Jalankan server
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Jalankan test
.\.venv\Scripts\python.exe -m pytest tests -v

# Jalankan eksperimen riset
.\.venv\Scripts\python.exe -m research.experiments.run_experiment

# Seed ulang data demo peserta (Budi Santoso & tiket aktif)
.\.venv\Scripts\python.exe scripts/seed_demo_participant.py
```

Atau jika virtual environment diaktifkan terlebih dahulu:
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Seed Accounts for Testing

| Role | Email | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@smartticket.com` | `admin123` | `/admin/dashboard`, `/events` management, Model Info |
| **Event Operator** | `operator@smartticket.com` | `operator123` | `/operator/dashboard`, `/operator/scanner` |
| **Participant** | *Create new via `/auth/register`* | *user choice* | Event registration, 9-pose face capture, digital tickets |

---

## 6. Project Directory Map

```
smart-event-ticketing/
├── app/
│   ├── main.py                     # FastAPI server entry point & startup seeder
│   ├── config.py                   # Pydantic configuration & environment settings
│   ├── cv/                         # Computer Vision Pipeline
│   │   ├── face_detector.py        # OpenCV Haar Cascade face detector & ROI extraction
│   │   ├── preprocessing.py        # Grayscale (NTSC/BT.601), 128x128 resizing, normalization
│   │   ├── quality_check.py        # Laplacian blur, brightness, centering validation
│   │   ├── hog_extractor.py        # 8,100-dim HOG feature extraction & math gradients
│   │   └── visualization.py        # Colormapped gradient & intermediate visual generation
│   ├── ml/                         # Machine Learning Modules
│   │   ├── knn_model.py            # Euclidean distance KNN classifier
│   │   ├── pso_optimizer.py        # Particle Swarm Optimization hyperparameter tuning
│   │   ├── threshold.py            # Calibrated rejection threshold & unknown face handler
│   │   ├── inference.py            # Production facial verification engine
│   │   ├── dataset.py              # Dynamic feature gallery persistence (.npz)
│   │   └── model_manager.py        # Active model versions and evaluation report persistence
│   ├── database/                   # Database models and SQLAlchemy connection
│   ├── routes/                     # FastAPI route controllers (Auth, Events, Check-in, CV Lab, Admin)
│   ├── security/                   # Argon2id password hashing, signed sessions, SHA-256 tokens
│   ├── templates/                  # Modular Jinja2 HTML templates
│   └── static/                     # CSS design tokens, Vanilla JS controllers (Camera, QR, Lab)
├── research/
│   ├── experiments/run_experiment.py # Reproducible scientific experiment comparing KNN vs PSO-KNN
│   └── results/                    # Generated charts (pso_convergence.png, model_comparison.png)
├── storage/                        # Private biometric storage (.gitignore protected)
├── docs/                           # Architecture, methodology, flowcharts, testing reports
└── tests/                          # Automated Pytest suite (CV, ML, Ticketing, Concurrency)
```

---

## 7. Computer Vision & ML Laboratory

Navigate to **`/cv-lab`** in the application to inspect the real-time pipeline on any webcam frame or uploaded image:
1. Face bounding box and cropped ROI
2. 128×128 grayscale and contrast equalized images
3. Horizontal gradient ($G_x$) and Vertical gradient ($G_y$)
4. Gradient magnitude ($M$) and gradient orientation ($\theta$) maps
5. HOG orientation vectors and 8,100-dimensional vector statistics
6. Live KNN distance computation and calibrated threshold verdict

