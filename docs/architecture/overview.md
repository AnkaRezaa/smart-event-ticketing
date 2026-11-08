# Architecture Overview

The **Smart Event Ticketing System** is designed as a clean modular monolith adhering to separation of concerns between web presentation, business logic, image processing, and machine learning inference.

---

## 1. High-Level Architecture

```
[ Client Browser (HTML5 / Vanilla JS / Canvas / MediaDevices) ]
                      |
                      | HTTP / JSON API / Cookies
                      v
            [ FastAPI Web Backend ]
          /           |           \
         /            |            \
        v             v             v
[ Jinja2 HTML ]  [ Services ]  [ CV & ML Engine ]
(Presentation)   (Auth/Tickets) (OpenCV/HOG/KNN/PSO)
                      |             |
                      v             v
             [ Relational DB ]   [ Private Biometrics ]
             (MySQL / SQLite)    (Encrypted/Protected)
```

---

## 2. Directory Structure & Responsibilities

* **`app/cv/`**: Independent computer vision modules for face detection (`face_detector.py`), preprocessing & grayscale conversion (`preprocessing.py`), heuristic quality checks (`quality_check.py`), HOG feature extraction (`hog_extractor.py`), and real-time visualization colormaps (`visualization.py`).
* **`app/ml/`**: Machine learning classifiers and optimizers, including KNN with Euclidean distance (`knn_model.py`), Particle Swarm Optimization (`pso_optimizer.py`), distance rejection thresholds (`threshold.py`), production verification (`inference.py`), and dynamic gallery management (`dataset.py`).
* **`app/services/`**: Transactional business logic handling authentication, event capacities, biometric enrollment consent, single-use ticket issuance, and atomic check-in transitions.
* **`app/routes/`**: FastAPI endpoints managing session-based HTML views and RESTful JSON APIs.
* **`app/templates/`**: Native Jinja2 components and pages for participants, operators, administrators, and the CV Lab.
* **`research/`**: Reproducible training benchmarks, experiments, and visualization output comparing baseline KNN and PSO-KNN.

