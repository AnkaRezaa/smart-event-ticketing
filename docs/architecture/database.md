# Database Architecture & Entity Relationship Design

The database schema is implemented with SQLAlchemy 2.0 and supports MySQL 8.0 (using PyMySQL) and SQLite.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o{ registrations : "registers"
    users ||--o| face_profiles : "owns"
    users ||--o{ tickets : "receives"
    users ||--o{ checkin_sessions : "conducts as operator"
    users ||--o{ checkin_logs : "records as operator"
    users ||--o{ operator_assignments : "assigned to"

    events ||--o{ registrations : "contains"
    events ||--o{ tickets : "admits"
    events ||--o{ checkin_sessions : "operates at"
    events ||--o{ operator_assignments : "staffed by"

    registrations ||--o| tickets : "issues"

    face_profiles ||--o{ face_samples : "contains"
    face_samples ||--o| face_features : "extracts to"

    tickets ||--o{ checkin_sessions : "authorized via"
    tickets ||--o{ checkin_logs : "audited by"

    model_versions ||--o{ checkin_logs : "evaluates"

    users {
        string id PK
        string name
        string email UK
        string password_hash
        string role
        datetime created_at
        datetime updated_at
    }

    events {
        string id PK
        string title
        text description
        string location
        datetime start_at
        datetime end_at
        int capacity
        string status
        datetime created_at
    }

    registrations {
        string id PK
        string event_id FK
        string user_id FK
        string status
        datetime registered_at
    }

    face_profiles {
        string id PK
        string user_id FK
        string enrollment_status
        datetime consent_timestamp
        string feature_version
    }

    face_samples {
        string id PK
        string profile_id FK
        string image_reference
        string pose_label
        string quality_status
        datetime created_at
    }

    face_features {
        string id PK
        string sample_id FK
        string feature_reference
        string feature_version
        datetime created_at
    }

    tickets {
        string id PK
        string event_id FK
        string registration_id FK
        string user_id FK
        string token_hash UK
        string status
        datetime issued_at
        datetime used_at
    }

    checkin_sessions {
        string id PK
        string ticket_id FK
        string operator_id FK
        string event_id FK
        datetime expires_at
        string status
    }

    checkin_logs {
        string id PK
        string ticket_id FK
        string operator_id FK
        string result
        string failure_reason
        string model_version_id FK
        datetime created_at
    }

    model_versions {
        string id PK
        string algorithm
        text hog_config
        text knn_config
        text pso_config
        float threshold
        datetime activated_at
    }
```

---

## 2. Table Specifications & Security Design

### `users`
* Primary identity store with role-based access control (`participant`, `operator`, `admin`).
* Passwords hashed using Argon2id with recommended parameters (time cost 3, memory cost 64MB, parallelism 4).

### `face_profiles`, `face_samples`, and `face_features`
* Decoupled from public user tables.
* Stores relative paths to private local storage (`storage/private_faces/` and `storage/features/`), ensuring raw biometric facial images are never exposed via public static URLs.
* Tracks consent timestamp and feature versions.

### `tickets`
* **Single-Use Enforcement:** Holds status enum (`ACTIVE`, `USED`, `CANCELLED`).
* **Token Protection:** The QR Code contains a 48-byte URL-safe cryptographic token. The database stores only the SHA-256 hash (`token_hash`), preventing token reconstruction from database dumps.
* **Atomic Consumption:** Updates from `ACTIVE` to `USED` are guarded by conditional update constraints, ensuring concurrent QR scans cannot enter the venue twice.

### `checkin_sessions`
* Ephemeral sessions with 3-minute sliding expirations preventing abandoned or hijacked scans.

