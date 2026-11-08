# API Documentation

This document describes the JSON API endpoints powering the camera, enrollment, QR validation, and biometric verification workflows.

---

## 1. Authentication Endpoints

### `POST /auth/login`
Authenticates a user and sets an HTTP-only secure signed session cookie.
* **Form Parameters:**
  * `email` (string): User email address.
  * `password` (string): Plaintext password.
* **Response:** 302 Redirect to role dashboard.

### `POST /auth/register`
Registers a new user account with role assignment.
* **Form Parameters:**
  * `name` (string): Full name.
  * `email` (string): Unique email address.
  * `password` (string): Password (min 6 characters).
  * `role` (string): One of `participant`, `operator`, `admin`.

---

## 2. Facial Enrollment Endpoints

### `POST /api/enrollment/sample`
Validates face quality, crops normalized ROI, extracts HOG descriptors, and stores the facial sample.
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "image_base64": "data:image/jpeg;base64,...",
    "pose_label": "frontal_1"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "success": true,
    "sample_id": "8b5d3a3f-...",
    "pose_label": "frontal_1",
    "total_samples": 1,
    "message": "Sample captured and feature vector extracted successfully"
  }
  ```

### `POST /api/enrollment/complete`
Confirms biometric consent and marks facial enrollment as complete, triggering active ticket issuance.
* **Request Body:**
  ```json
  {
    "consent": true
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Biometric enrollment confirmed"
  }
  ```

---

## 3. Venue Check-In & Verification Endpoints

### `POST /api/checkin/validate-qr`
Validates ticket QR token status and starts a short-lived 3-minute check-in session.
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "qr_token": "48_char_urlsafe_cryptographic_token"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "valid": true,
    "session_id": "4b68e920-...",
    "ticket_id": "1d867c4e-...",
    "event_title": "Summer Tech Festival 2026",
    "owner_name": "Alice Doe",
    "owner_id": "user-uuid",
    "expires_at": "2026-11-09T02:15:00"
  }
  ```

### `POST /api/checkin/verify-face`
Performs live face verification against the ticket owner's enrolled samples and atomically transitions ticket status to `USED`.
* **Headers:** `Content-Type: application/json`
* **Request Body:**
  ```json
  {
    "session_id": "4b68e920-...",
    "image_base64": "data:image/jpeg;base64,..."
  }
  ```
* **Success Response (200 OK - Granted):**
  ```json
  {
    "authorized": true,
    "verdict": "ACCESS GRANTED",
    "message": "Face verified successfully. Welcome to the venue!",
    "owner_name": "Alice Doe",
    "event_title": "Summer Tech Festival 2026",
    "checkin_time": "2026-11-09 02:12:34",
    "owner_distance": 0.3821,
    "threshold": 0.6327,
    "confidence": 0.7235
  }
  ```

---

## 4. Computer Vision Lab Endpoints

### `POST /api/cv-lab/inspect`
Executes full OpenCV pipeline on arbitrary input image and returns base64 images of all intermediate processing stages along with HOG vector statistics.
* **Request Body:**
  ```json
  {
    "image_base64": "data:image/jpeg;base64,..."
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "success": true,
    "latency_ms": 142.5,
    "visualizations": {
      "annotated_image": "data:image/jpeg;base64,...",
      "roi_image": "data:image/jpeg;base64,...",
      "gray_image": "data:image/jpeg;base64,...",
      "equalized_image": "data:image/jpeg;base64,...",
      "gx_image": "data:image/jpeg;base64,...",
      "gy_image": "data:image/jpeg;base64,...",
      "magnitude_image": "data:image/jpeg;base64,...",
      "orientation_image": "data:image/jpeg;base64,...",
      "hog_image": "data:image/jpeg;base64,...",
      "feature_summary": {
        "dimension": 8100,
        "min": 0.0,
        "max": 0.2,
        "mean": 0.0421,
        "std": 0.0512,
        "sparsity_zeros_pct": 21.4,
        "first_20_values": [0.05, 0.12, ...]
      }
    },
    "ml_decision": {
      "predicted_user_id": "...",
      "predicted_label": "John Doe",
      "min_distance": 0.412,
      "active_threshold": 0.6327,
      "is_within_threshold": true,
      "confidence": 0.7082
    }
  }
  ```

