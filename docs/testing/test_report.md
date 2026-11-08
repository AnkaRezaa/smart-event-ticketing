# Automated Testing & Security Verification Report

This report documents the verification, automated testing, and security evaluation conducted on the Smart Event Ticketing System codebase.

---

## 1. Test Suite Summary

* **Framework:** Pytest 9.2.0 on Python 3.10.6 (Windows 10/11)
* **Total Tests Executed:** 12
* **Passed:** 12
* **Failed:** 0
* **Execution Time:** ~12.4 seconds

```
============================= test session starts =============================
platform win32 -- Python 3.10.6, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\laragon\www\smart-event-ticketing
plugins: anyio-4.16.0
collected 12 items

tests\test_cv_pipeline.py .....                                          [ 41%]
tests\test_ml_models.py ....                                             [ 75%]
tests\test_ticketing_and_checkin.py ...                                  [100%]

============================= 12 passed in 12.40s =============================
```

---

## 2. Test Coverage Breakdown

### 2.1 Computer Vision Pipeline (`tests/test_cv_pipeline.py`)
| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_image_loader_b64` | Verifies base64 data URI encoding, parsing, and OpenCV BGR decoding. | **PASSED** |
| `test_grayscale_formula` | Strictly tests adherence to $Gray = 0.2989R + 0.5870G + 0.1140B$. | **PASSED** |
| `test_resizing_and_preprocessing` | Validates standard 128×128 spatial resizing and histogram equalization. | **PASSED** |
| `test_hog_feature_dimension` | Asserts extracted descriptor length is strictly **8,100 numerical values**. | **PASSED** |
| `test_quality_checks` | Tests Laplacian variance blur estimation and mean luminance checks. | **PASSED** |

### 2.2 Machine Learning & Optimization (`tests/test_ml_models.py`)
| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_knn_fit_and_predict` | Verifies KNN fitting, Euclidean nearest neighbor distance, and voting. | **PASSED** |
| `test_claimed_identity_distance` | Verifies distance computation against enrolled samples of the claimed ticket owner. | **PASSED** |
| `test_threshold_rejection` | Validates rejection of unknown/distant faces when distance exceeds threshold $\tau$. | **PASSED** |
| `test_pso_optimizer` | Verifies particle swarm convergence, velocity clamping, and parameter bounds. | **PASSED** |

### 2.3 Ticketing Security & Check-In Enforcement (`tests/test_ticketing_and_checkin.py`)
| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_password_argon2` | Validates secure password hashing using Argon2id. | **PASSED** |
| `test_qr_token_unpredictability` | Confirms cryptographic uniqueness and SHA-256 database token hashing. | **PASSED** |
| `test_ticket_issuance_and_single_use` | Validates complete ticket lifecycle: registration, mandatory enrollment gating, active QR scan, check-in consumption, and strict rejection of reused tickets. | **PASSED** |

---

## 3. Security & Concurrency Verification

1. **Replay & Double-Spending Protection:**
   The ticket state machine (`ACTIVE` $\rightarrow$ `USED` $\rightarrow$ `CANCELLED`) enforces single entrance. The check-in service executes a conditional atomic update:
   ```python
   stmt = (
       update(Ticket)
       .where(Ticket.id == ticket.id)
       .where(Ticket.status == TicketStatus.ACTIVE)
       .values(status=TicketStatus.USED, used_at=now)
   )
   ```
   If two concurrent turnstile scanners read the same QR ticket at the exact millisecond, database row locking ensures only one query succeeds with `rowcount == 1`. The second attempt fails with `CONCURRENT_USAGE` and is flagged as ACCESS DENIED.

2. **Biometric Privacy Safeguard:**
   Captured facial images are stored strictly in private directories (`storage/private_faces/`) inaccessible to public HTTP routes. Only authenticated administrative users or verification pipelines can access these images.

3. **Presentation Attack / Anti-Spoofing Note:**
   As noted in Hardjianto et al. (2026), classical HOG-KNN descriptors alone do not establish passive 3D liveness against high-resolution printed photos. The system relies on supervised operator turnstile verification.

