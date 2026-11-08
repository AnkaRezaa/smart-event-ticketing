# MASTER IMPLEMENTATION PROMPT
## SMART EVENT TICKETING SYSTEM — FACE RECOGNITION USING HOG, KNN & PSO

**Target AI Coding Agent:** OpenAI Codex / Google Antigravity  
**Project Type:** Full-Stack Web Application + Computer Vision + Machine Learning  
**Academic Focus:** Pengolahan Citra dan Visi Komputer (PCVK)  
**Frontend:** Native HTML5, CSS3, Vanilla JavaScript  
**Backend:** Python FastAPI  
**Database:** PostgreSQL  
**Machine Learning:** Histogram of Oriented Gradients, K-Nearest Neighbor, Particle Swarm Optimization

---

# 1. YOUR ROLE

Act as a Senior Full-Stack Engineer, Computer Vision Engineer, Machine Learning Engineer, Database Architect, Software Security Engineer, and Academic Research Assistant.

Your primary responsibility is to build a complete, functional, modular, and maintainable event ticketing application that integrates QR Code authentication with face recognition.

This is an academic project emphasizing image processing and machine learning. Therefore, actual implementation of computer vision algorithms is mandatory.

Do not create only a frontend prototype.

Do not use mock facial recognition results as the final implementation.

Do not replace HOG, KNN, or PSO with cloud facial recognition services, pretrained FaceNet, ArcFace, DeepFace, or other facial recognition classifiers.

Implement the requested algorithms using Python and established machine learning libraries.

All code should be organized, documented, and testable.

## Mandatory Development Principles

1. Build actual working features, not decorative UI.
2. Use clean and maintainable code.
3. Avoid unnecessary dependencies.
4. Separate application logic from machine learning logic.
5. Ensure all frontend features communicate with real backend endpoints.
6. Use a relational database for persistent application data.
7. Prioritize the scientific computer vision implementation.
8. Preserve the correct machine learning workflow.
9. Implement security and data validation.
10. Test major features after implementation.
11. Document all important engineering decisions.
12. Do not fabricate experimental results.
13. Do not claim a feature is working without verification.
14. Do not stop after creating project scaffolding.
15. Continue through the implementation phases whenever the working environment permits.

# 2. PROJECT DESCRIPTION

Project Name:

**Smart Event Ticketing System with QR Code and Face Recognition Using HOG, KNN, and PSO**

Develop a web-based ticketing system for events, seminars, concerts, festivals, and other organized activities.

The system must verify that the person entering the venue is the legitimate owner of the registered ticket.

Authentication consists of two stages:

**First authentication: QR Code**

The system validates the digital ticket.

**Second authentication: Face Recognition**

The system verifies whether the captured face matches the identity associated with that ticket.

Entrance is permitted only when both verification stages succeed.

Every ticket must be valid for one successful entrance only.

The system must prevent ticket reuse, unauthorized access, and identity mismatches.

The facial recognition pipeline must utilize:

- HOG for facial feature extraction.
- KNN for facial identity classification.
- PSO for optimizing selected KNN parameters.

# 3. SCIENTIFIC REFERENCE

The main reference paper is:

"Attendance System with Face Recognition Using K-Nearest Neighbor, Particle Swarm Optimization, and Histogram of Oriented Gradients."

Journal of Embedded System Security and Intelligent Systems, Volume 7, Number 4, 2026.

The original PDF must be treated as the primary methodological reference.

Search the project workspace for the PDF in `docs/references/`.

If the PDF is absent, explicitly report that the reference must be supplied. Continue implementing clearly identified engineering assumptions without falsely attributing them to the paper.

The study applies HOG, KNN, and PSO to employee attendance recognition.

Reported details include:

- 20 enrolled employees.
- 180 enrollment images.
- Nine facial images per employee.
- 27 evaluation images.
- 18 true positives.
- Seven true negatives.
- Zero false positives.
- Two false negatives.
- Approximately 92.6% reported evaluation accuracy.

Important methodological limitations:

1. The study's accuracy cannot automatically be applied to this project.
2. The study does not completely disclose all final KNN and PSO parameters.
3. Recognition thresholds must be determined experimentally.
4. The study does not demonstrate production-grade anti-spoofing.
5. PSO superiority over a separately evaluated baseline KNN has not been conclusively established by the reported experiment.
6. The original system is an attendance prototype, not a concert ticketing system.

The ticket registration, QR authentication, and single-use entrance mechanisms are project-specific engineering adaptations.

Separate publication-derived methodology from implementation assumptions.

# 4. REQUIRED TECHNOLOGY STACK

## 4.1 Frontend

Use strictly:

- HTML5.
- CSS3.
- Vanilla JavaScript ES6+.
- Jinja2 server-side templates.
- Native Fetch API.
- Native browser MediaDevices API.
- Browser Canvas API.
- CSS Grid.
- CSS Flexbox.

Do not use:

- React.
- Vue.
- Angular.
- Next.js.
- Nuxt.
- Vite.
- Tailwind CSS.
- jQuery.
- TypeScript.
- JavaScript SPA frameworks.

Avoid Node.js and npm as required runtime dependencies.

Use modular JavaScript files and reusable Jinja2 template components.

Small, well-maintained JavaScript libraries may be included for specific functionality such as QR scanning, preferably as locally bundled static dependencies.

All normal page rendering must work through FastAPI and Jinja2.

## 4.2 Backend

Use:

- Python 3.11+.
- FastAPI.
- Uvicorn.
- Jinja2.
- Pydantic.
- SQLAlchemy.
- Alembic.
- PostgreSQL.
- Argon2id password hashing.
- Secure cookie-based sessions.
- CSRF protection for state-changing browser requests.

Use the framework and libraries consistently.

## 4.3 Image Processing

Use:

- OpenCV.
- NumPy.
- scikit-image.
- Pillow where necessary.

## 4.4 Machine Learning

Use:

- scikit-learn.
- NumPy.
- pandas.
- PySwarms or a tested custom PSO implementation.
- joblib.
- matplotlib.

## 4.5 Research and Testing

Use:

- Jupyter Notebook.
- Pytest.
- Playwright Python where browser automation is needed.
- Ruff for Python linting.
- Docker Compose for optional reproducible local development.

The application must also support ordinary local Python development without requiring Docker.

# 5. APPLICATION ARCHITECTURE

Use a modular monolithic architecture.

FastAPI serves two responsibilities:

1. Rendering HTML pages through Jinja2.
2. Providing JSON API endpoints for asynchronous camera, enrollment, QR, and verification functionality.

Machine learning inference must run on the Python backend.

Do not execute the main HOG-KNN-PSO recognition model inside the browser.

## Architecture

Browser:

HTML + CSS + JavaScript  
↓  
FastAPI + Jinja2  
↓  
Application Services  
↓  
PostgreSQL + Computer Vision / ML Modules

The browser handles:

- Page navigation.
- User forms.
- Camera permissions.
- Webcam preview.
- Image capture.
- Enrollment progress.
- QR scanning.
- Verification feedback.

The backend handles:

- Authentication.
- Authorization.
- Event registration.
- Ticket creation.
- QR validation.
- Image preprocessing.
- HOG feature extraction.
- KNN prediction.
- Facial similarity verification.
- Ticket consumption.
- Audit logging.

# 6. PROJECT DIRECTORY STRUCTURE

Use the following structure as the initial architecture.

    smart-event-ticketing/
    │
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   │
    │   ├── routes/
    │   │   ├── auth.py
    │   │   ├── events.py
    │   │   ├── registration.py
    │   │   ├── enrollment.py
    │   │   ├── tickets.py
    │   │   ├── checkin.py
    │   │   ├── admin.py
    │   │   └── cv_lab.py
    │   │
    │   ├── database/
    │   │   ├── connection.py
    │   │   └── models.py
    │   │
    │   ├── schemas/
    │   ├── repositories/
    │   ├── services/
    │   ├── security/
    │   │
    │   ├── cv/
    │   │   ├── image_loader.py
    │   │   ├── face_detector.py
    │   │   ├── preprocessing.py
    │   │   ├── quality_check.py
    │   │   ├── hog_extractor.py
    │   │   └── visualization.py
    │   │
    │   ├── ml/
    │   │   ├── dataset.py
    │   │   ├── knn_model.py
    │   │   ├── pso_optimizer.py
    │   │   ├── threshold.py
    │   │   ├── inference.py
    │   │   ├── evaluation.py
    │   │   └── model_manager.py
    │   │
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── components/
    │   │   ├── public/
    │   │   ├── participant/
    │   │   ├── operator/
    │   │   ├── admin/
    │   │   └── cv_lab/
    │   │
    │   └── static/
    │       ├── css/
    │       │   ├── variables.css
    │       │   ├── base.css
    │       │   ├── components.css
    │       │   └── pages/
    │       ├── js/
    │       │   ├── api.js
    │       │   ├── camera.js
    │       │   ├── enrollment.js
    │       │   ├── qr-scanner.js
    │       │   ├── verification.js
    │       │   └── cv-lab.js
    │       ├── images/
    │       └── vendor/
    │
    ├── research/
    │   ├── datasets/
    │   ├── notebooks/
    │   ├── training/
    │   ├── experiments/
    │   ├── evaluation/
    │   └── results/
    │
    ├── storage/
    │   ├── private_faces/
    │   ├── features/
    │   └── model_artifacts/
    │
    ├── tests/
    ├── alembic/
    ├── docs/
    │   ├── references/
    │   ├── architecture/
    │   ├── methodology/
    │   └── testing/
    │
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── docker-compose.yml
    └── README.md

Keep sensitive files inside private storage.

Exclude biometric images, real participant datasets, secrets, and trained model artifacts containing biometric references from public Git repositories by default.

# 7. USER ROLES

Implement three primary user roles.

## 7.1 Participant

Capabilities:

- Create account.
- Log in.
- Browse events.
- View event details.
- Register for events.
- Complete facial enrollment.
- View enrollment status.
- Receive QR tickets.
- View ticket history.
- View personal profile.
- Review biometric data consent.
- Request appropriate deletion of biometric data.

## 7.2 Event Operator

Capabilities:

- Log in to operator dashboard.
- Select assigned events.
- Activate venue scanner.
- Scan QR Codes.
- Perform facial verification.
- View verification results.
- View entrance records.
- Request manual review for unresolved failures.

Operators may access only assigned events.

## 7.3 Administrator

Capabilities:

- Manage events.
- Manage registrations.
- Assign operators.
- View ticket statistics.
- View check-in records.
- Access machine learning evaluation reports.
- View active model configuration.
- Activate validated model versions.
- Manage application settings and authorized retention operations.

Use backend role-based access control.

# 8. COMPLETE SYSTEM WORKFLOW

The complete workflow must follow this sequence.

## PHASE A — PARTICIPANT REGISTRATION

1. User accesses the website.
2. User registers or logs in.
3. User selects an event.
4. System checks whether registration is available.
5. User submits event registration.
6. System checks capacity and duplicate registrations.
7. System requests biometric enrollment consent.
8. User proceeds to facial enrollment.
9. System captures facial samples.
10. System validates image quality.
11. System processes the images using the computer vision pipeline.
12. System extracts HOG descriptors.
13. System stores labeled face features.
14. System registers the new identity in the eligible feature gallery.
15. System confirms completed enrollment.
16. System issues one unique digital ticket.
17. System generates the ticket QR Code.

If enrollment fails, the system must not issue an ACTIVE ticket.

## PHASE B — VENUE ENTRANCE

1. Participant arrives at the venue.
2. Operator opens the scanner.
3. Operator scans the ticket QR Code.
4. Backend verifies token validity.
5. Backend checks event eligibility.
6. Backend checks whether ticket status is ACTIVE.
7. Backend creates a short-lived verification session.
8. Operator initiates facial verification.
9. Camera captures the participant's face.
10. Backend detects the face.
11. Backend preprocesses the image.
12. Backend extracts HOG descriptors.
13. KNN predicts the facial identity.
14. Backend compares prediction with ticket owner.
15. Backend checks facial distance threshold.
16. Backend checks the verification session.
17. If the match is valid, backend atomically consumes the ticket.
18. System displays ACCESS GRANTED.
19. If verification fails, system displays ACCESS DENIED.
20. Failed verification must not consume the ticket.

## PHASE C — SINGLE-USE TICKET

Tickets must follow an explicit state model:

- ACTIVE.
- USED.
- CANCELLED.

The server must also enforce expiration according to event timing.

Once a ticket changes from ACTIVE to USED, it must not become ACTIVE again through ordinary check-in operations.

The database must prevent concurrent QR scans from successfully consuming the same ticket twice.

# 9. FACIAL ENROLLMENT SYSTEM

Build an interactive facial enrollment page.

The page must contain:

- Live webcam preview.
- Camera activation button.
- Camera permission handling.
- Face detection indicator.
- Face position instructions.
- Capture button.
- Enrollment progress.
- Captured sample previews.
- Retake sample functionality.
- Image quality feedback.
- Completion confirmation.

Capture approximately nine acceptable face samples per participant.

Suggested facial variations:

1. Frontal neutral face.
2. Slight left rotation.
3. Slight right rotation.
4. More pronounced left variation.
5. More pronounced right variation.
6. Slight upward orientation.
7. Slight downward orientation.
8. Mild expression variation.
9. Additional frontal sample.

Do not claim these exact nine positions are prescribed in full by the research paper.

Image quality validation must check:

- Face detected.
- Exactly one face in the capture.
- Face positioned inside the expected region.
- Adequate resolution.
- Acceptable blur level.
- Adequate brightness.
- Valid image format.
- Valid dimensions.

Define practical initial thresholds and document them as engineering choices.

Never create fake enrollment success results.

# 10. COMPUTER VISION PIPELINE

This is a critical academic component.

Implement the pipeline in independent Python functions.

The pipeline must be reusable for enrollment and verification.

## Stage 1 — Image Acquisition

Receive the image captured from the browser.

Validate file content, size, decoding, and format.

## Stage 2 — Face Detection

Implement face detection using OpenCV.

A Haar Cascade detector is acceptable as the initial classical computer vision implementation.

Extract the facial bounding box.

Reject invalid frames.

## Stage 3 — Region of Interest

Crop the detected face.

Use consistent cropping and alignment rules.

## Stage 4 — Image Resizing

Resize facial ROI to 128 × 128 pixels.

## Stage 5 — Grayscale Conversion

Convert the input to grayscale.

Reference formula:

Gray = 0.2989R + 0.5870G + 0.1140B

Ensure correct handling of BGR images from OpenCV.

## Stage 6 — Preprocessing

Apply a consistent preprocessing sequence.

Possible operations include intensity normalization and controlled lighting adjustment.

Do not apply aggressive image transformations without justification.

## Stage 7 — HOG Feature Extraction

Calculate gradient values and orientation histograms.

## Stage 8 — Feature Vector Generation

Generate a fixed-length numerical descriptor.

## Stage 9 — Feature Storage

Save extracted features and identity labels.

Store the image-processing configuration version.

## Stage 10 — KNN Inference

Feed HOG features into the trained or fitted KNN recognition system.

All enrollment and verification images must use compatible preprocessing and HOG configurations.

# 11. HISTOGRAM OF ORIENTED GRADIENTS

Implement HOG as the primary feature extraction algorithm.

Use scikit-image for the production feature extractor, while also developing educational visualizations demonstrating the calculations.

Initial experimental configuration:

- Image size: 128 × 128.
- Orientations: 9.
- Pixels per cell: 8 × 8.
- Cells per block: 2 × 2.
- Block normalization: L2-Hys.

Expected feature vector dimension:

8100 numerical values.

Validate the dimensionality in automated tests.

## Required HOG Processing

1. Input grayscale image.
2. Calculate horizontal gradient.
3. Calculate vertical gradient.
4. Calculate gradient magnitude.
5. Calculate gradient orientation.
6. Divide the image into cells.
7. Accumulate orientation histograms.
8. Normalize blocks.
9. Concatenate descriptors.
10. Return the final feature vector.

## Mathematical Equations

Horizontal gradient:

Gx = I(x+1,y) - I(x-1,y)

Vertical gradient:

Gy = I(x,y+1) - I(x,y-1)

Magnitude:

M = sqrt(Gx² + Gy²)

Orientation:

θ = atan2(Gy, Gx)

Use mathematically correct implementations and clearly document boundary handling.

## Required HOG Visualizations

Implement actual image processing visualizations showing:

- Original image.
- Facial bounding box.
- Cropped facial ROI.
- Resized face.
- Grayscale image.
- Horizontal gradient.
- Vertical gradient.
- Gradient magnitude.
- Gradient orientation.
- HOG visualization.
- Histogram representation.
- Feature vector preview.

The Computer Vision Lab page and Jupyter Notebook must use actual computed outputs.

Do not display unrelated decorative images as HOG results.

# 12. K-NEAREST NEIGHBOR IMPLEMENTATION

Implement KNN using scikit-learn.

The input must be the extracted HOG feature vector.

Use Euclidean distance as the primary metric, following the methodological reference.

Euclidean distance:

d(x,y) = sqrt(Σ(xᵢ-yᵢ)²)

## Required KNN Functions

- Create labeled feature gallery.
- Fit KNN classifier.
- Select nearest neighbors.
- Calculate Euclidean distances.
- Predict registered identity.
- Identify unknown faces.
- Verify claimed identity.
- Save model configuration.
- Load and update active model references.

## Unknown Face Handling

A standard KNN classifier assigns the nearest known identity even when a face is unfamiliar.

Therefore, implement a calibrated rejection threshold.

The system must support UNKNOWN results.

Unknown-face rejection is mandatory.

Do not accept every nearest-neighbor prediction.

## QR-Claimed Identity Matching

For entrance verification:

1. Retrieve owner identity from validated QR ticket.
2. Process the captured live face.
3. Compute HOG descriptors.
4. Run KNN identity classification.
5. Verify predicted identity equals ticket owner.
6. Independently check the distance to appropriate enrolled samples of the claimed identity.
7. Apply the calibrated threshold.
8. Reject when any required identity condition fails.

A successful KNN classification alone must not authorize entrance.

Do not confuse classification distance with calibrated probability.

## Dynamic Enrollment

KNN is instance-based.

When a new participant completes enrollment:

- Add validated labeled HOG descriptors to the permitted gallery.
- Refresh the relevant recognition index or fitted KNN model.
- Preserve preprocessing compatibility.
- Ensure that newly enrolled participants can be recognized.
- Avoid retraining the PSO optimizer after every individual registration.

Use model or gallery versioning to maintain consistency during verification.

# 13. PARTICLE SWARM OPTIMIZATION

Implement PSO to optimize selected KNN parameters.

PSO must not be described as a face detector or facial classifier.

## Experimental Models

Implement two comparable models:

**Model A: HOG + KNN Baseline**

Use a predefined, documented KNN configuration.

Example initial k value: 3.

**Model B: HOG + KNN Optimized by PSO**

Use PSO to search for improved KNN parameters.

The minimum optimization target is:

- Number of neighbors, k.

Optional research extension:

- Facial rejection threshold.

If optimizing both, describe the search ranges, parameter representation, and constraints.

## PSO Algorithm Workflow

1. Define optimization parameters.
2. Define the search space.
3. Initialize particle positions.
4. Initialize particle velocities.
5. Evaluate each particle configuration.
6. Calculate fitness.
7. Update personal best.
8. Update global best.
9. Update velocity.
10. Update position.
11. Repeat until stopping criteria are met.
12. Save optimized parameters.

Implement standard PSO equations:

v(t+1) = w·v(t) + c1·r1·(pbest-x(t)) + c2·r2·(gbest-x(t))

x(t+1) = x(t) + v(t+1)

Where:

- w = inertia weight.
- c1 = cognitive coefficient.
- c2 = social coefficient.
- r1, r2 = random factors.
- pbest = personal best.
- gbest = global best.

Store optimizer configurations and random seeds.

Use appropriate validation-based fitness.

Penalize false acceptance appropriately.

Do not automatically assume PSO performs better than baseline KNN.

## Required PSO Outputs

- Initial candidate parameters.
- Optimized parameters.
- Best fitness.
- Fitness history.
- Iteration count.
- Comparison with baseline KNN.
- Convergence visualization.

# 14. MACHINE LEARNING TRAINING AND EVALUATION

Create reproducible Python training and evaluation scripts.

## Dataset Requirements

Support labeled face datasets.

The project must not fabricate genuine face datasets.

Collect actual participant images only with proper consent.

For automated application testing, synthetic feature vectors may be used, but synthetic feature tests are not evidence of biometric accuracy.

## Data Partitioning

Use:

- Training set.
- Validation set.
- Test set.

Avoid data leakage.

Keep images captured from the same frame or near-identical captures out of different subsets.

Where possible, use separate recording sessions for enrollment and testing.

Unknown-face tests must contain identities not registered in the training gallery.

Keep the final test set untouched during hyperparameter selection.

For known-identity evaluation, ensure tested identities have valid enrollment references while test images remain separate from enrollment samples.

## Evaluation Metrics

Calculate:

1. Accuracy.
2. Precision.
3. Recall.
4. F1-score.
5. Confusion matrix.
6. True positives.
7. True negatives.
8. False positives.
9. False negatives.
10. False Acceptance Rate.
11. False Rejection Rate.
12. Unknown-face rejection rate.
13. Average inference time.
14. HOG extraction time.
15. Model execution latency.

Clearly separate multi-class identity recognition from binary biometric acceptance evaluation.

## Required Research Visualizations

Generate:

- Confusion matrix.
- KNN baseline vs PSO-KNN accuracy comparison.
- Precision comparison.
- Recall comparison.
- F1-score comparison.
- PSO fitness convergence.
- Facial match-distance distribution.
- Threshold evaluation.
- FAR and FRR comparison.
- Inference latency comparison.

Create Jupyter Notebooks showing:

- Dataset inspection.
- Preprocessing.
- HOG extraction.
- KNN baseline training.
- PSO optimization.
- Evaluation.
- Final model comparison.

Results must be generated from executed experiments.

Do not fill tables with invented accuracy values.

# 15. TICKET AND QR CODE SYSTEM

Generate a unique digital ticket only after successful registration and facial enrollment.

Ticket information:

- Ticket ID.
- Event ID.
- Owner ID.
- Event title.
- Event date.
- Event location.
- Ticket status.
- Unique QR Code.
- Issue timestamp.

Generate cryptographically unpredictable QR tokens.

Store a secure token hash rather than the plaintext token in the database.

The QR payload must not contain sensitive biometric information.

Use Python for QR Code generation.

For QR scanning, use browser camera access with a suitable JavaScript QR decoder.

The native BarcodeDetector API can be used when available, but provide a compatible fallback because browser support varies.

## Ticket States

ACTIVE: available for one successful check-in.

USED: already consumed and no longer valid.

CANCELLED: not valid for entrance.

Enforce event expiration separately.

## Single-Use Enforcement

Perform a conditional, atomic ticket update within a backend transaction.

The final check-in must recheck ticket eligibility.

Only one concurrent verification can successfully consume the ticket.

Do not mark a ticket USED at initial QR validation.

Only successful facial verification followed by successful transactional ticket consumption may grant access.

# 16. VENUE CHECK-IN SYSTEM

Create an operator check-in interface.

## QR Scanning

The operator interface must:

- Activate the camera.
- Scan QR.
- Decode the token.
- Send the token to the backend.
- Display ticket validation state.
- Detect already-used or invalid tickets.
- Start a temporary verification session for valid tickets.

## Face Verification

After successful QR validation:

- Display face capture preview.
- Capture facial image.
- Send the captured image to the backend.
- Run preprocessing.
- Run HOG extraction.
- Run KNN.
- Apply claimed-identity verification.
- Apply calibrated threshold.
- Return verification result.

## Final Authorization

Display ACCESS GRANTED only after the backend atomically changes the ticket to USED.

Display ACCESS DENIED when verification fails.

The frontend must not be able to submit a trusted `face_verified=true` value.

Facial decisions and final ticket consumption must be controlled by the backend.

Use short-lived verification sessions, attempt limits, and event-operator authorization.

Handle session expiration, camera failure, network interruption, and duplicate scans.

# 17. BIOMETRIC SPOOFING LIMITATIONS

The reference method does not establish reliable resistance to printed-photo or video-replay attacks.

Do not claim HOG-KNN-PSO provides secure liveness detection.

For the academic prototype:

- Capture camera frames during supervised venue verification.
- Reject invalid and poor-quality captures.
- Implement controlled retry handling.
- Provide clearly identified experimental anti-spoofing tests.
- Document unresolved vulnerabilities.

An optional liveness module may be implemented as an additional research feature.

It must remain separate from the core HOG-KNN-PSO experiment.

Do not state that browser camera capture alone proves the person is physically present.

Provide an authorized, auditable manual review pathway for genuine users who fail automated recognition.

# 18. DATABASE DESIGN

Use PostgreSQL and SQLAlchemy.

Create tables for:

## users
- id
- name
- email
- password_hash
- role
- created_at
- updated_at

## events
- id
- title
- description
- location
- start_at
- end_at
- registration_open_at
- registration_close_at
- checkin_open_at
- checkin_close_at
- capacity
- status
- created_at

## registrations
- id
- event_id
- user_id
- status
- registered_at

## face_profiles
- id
- user_id
- enrollment_status
- consent_timestamp
- feature_version

## face_samples
- id
- profile_id
- image_reference
- pose_label
- quality_status
- created_at

## face_features
- id
- sample_id
- feature_reference
- feature_version
- created_at

## tickets
- id
- event_id
- registration_id
- user_id
- token_hash
- status
- issued_at
- used_at

## checkin_sessions
- id
- ticket_id
- operator_id
- event_id
- expires_at
- status

## checkin_logs
- id
- ticket_id
- operator_id
- result
- failure_reason
- model_version_id
- created_at

## model_versions
- id
- algorithm
- hog_config
- knn_config
- pso_config
- threshold
- artifact_reference
- created_at
- activated_at

## operator_assignments
- id
- operator_id
- event_id

## audit_logs
- id
- actor_id
- action
- resource_type
- resource_id
- created_at

Implement database relationships, constraints, and indexes.

Prevent duplicate event registrations.

Ensure enrollment and ticket issuance can be recovered safely after interrupted requests.

Use Alembic migrations.

# 19. BACKEND API DESIGN

Implement functional routes and documented JSON APIs.

## Authentication

- Registration.
- Login.
- Logout.
- Current authenticated user.
- Session handling.

## Events

- List events.
- Event details.
- Create event.
- Update event.
- Close registration.
- Retrieve event statistics.

## Registration

- Register participant.
- Retrieve registration.
- Check enrollment status.
- Complete registration.

## Facial Enrollment

- Start enrollment.
- Upload captured samples.
- Validate image quality.
- Extract features.
- Complete enrollment.
- Retrieve enrollment status.

## Tickets

- Retrieve tickets.
- Retrieve ticket details.
- Generate QR.
- Download ticket.
- Check ticket status.

## Check-in

- Validate QR.
- Start verification session.
- Submit captured face.
- Run face verification.
- Finalize authorized check-in.
- Retrieve check-in result.

## ML Administration

- Retrieve active model configuration.
- Retrieve evaluation metrics.
- Retrieve model version.
- Activate validated model.
- View experiment results.

Use consistent HTTP status codes.

Provide meaningful validation and failure messages.

Ensure all state-changing actions enforce authorization and CSRF protection where applicable.

# 20. FRONTEND DESIGN REQUIREMENTS

Build a professional and responsive website using native HTML, CSS, and JavaScript.

Design style:

- Modern.
- Clean.
- Minimal.
- Professional.
- Event and concert oriented.
- Responsive.
- Accessible.
- Visually consistent.

Use a design system implemented with CSS custom properties.

Example:

    :root {
      --primary: #2563eb;
      --background: #0b1120;
      --surface: #172033;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --success: #22c55e;
      --danger: #ef4444;
      --radius: 12px;
    }

These are initial design tokens and may be refined.

Use:

- CSS Grid.
- Flexbox.
- Reusable components.
- Responsive navigation.
- Clear form validation.
- Accessible semantic HTML.
- Loading states.
- Success and error states.

Avoid excessive animation.

## Required Public Pages

1. Landing Page.
2. Event Listing.
3. Event Details.
4. Login.
5. Register.

## Required Participant Pages

1. Dashboard.
2. Event Registration.
3. Face Enrollment.
4. Enrollment Result.
5. My Tickets.
6. Ticket Details.
7. Profile.
8. Registration History.

## Required Operator Pages

1. Operator Dashboard.
2. Select Event.
3. QR Scanner.
4. Face Verification.
5. Access Granted.
6. Access Denied.
7. Check-in History.

## Required Admin Pages

1. Dashboard.
2. Event Management.
3. Registration Management.
4. Operator Management.
5. Ticket Monitoring.
6. Check-in Analytics.
7. Model Information.
8. Machine Learning Evaluation.

Every page must have meaningful functionality.

Do not create empty dashboard cards or fake analytics.

# 21. COMPUTER VISION LAB PAGE

Create a dedicated page:

**Computer Vision & Machine Learning Laboratory**

This is an academically important feature.

The page must allow authorized users to inspect actual image-processing results.

## Image Processing Panel

Display:

- Original input image.
- Face detection.
- Bounding box.
- Cropped face.
- Resized face.
- Grayscale image.
- Gradient magnitude.
- HOG descriptor visualization.
- HOG feature-vector preview.

## Machine Learning Panel

Display:

- Active algorithm.
- HOG configuration.
- KNN configuration.
- Number of enrolled identities.
- Recognition result.
- Nearest-neighbor distances.
- Recognition threshold.
- Unknown-face decision.

## Research Evaluation Panel

Display actual generated experimental reports:

- Baseline KNN metrics.
- Optimized KNN metrics.
- Comparison charts.
- Confusion matrices.
- PSO convergence curve.
- Model version.

If real experiments have not yet been run, display a clearly labeled pending state.

Never manufacture metrics for a dashboard.

Only authorized administrators or research personnel may access private biometric processing information.

# 22. PRIVACY AND SECURITY

Implement reasonable protections for:

- Password hashing.
- Session management.
- Secure cookies.
- CSRF.
- XSS.
- Input validation.
- File validation.
- Role authorization.
- QR token secrecy.
- Ticket replay prevention.
- API rate limits.
- Secure biometric storage.
- Audit logging.
- Access control.
- Retention and deletion.
- Concurrent check-in protection.

Store facial images outside publicly accessible static directories.

Avoid unnecessary long-term retention of original images.

Document the biometric data lifecycle.

Obtain explicit participant consent.

Use HTTPS for production camera access.

Keep passwords, tokens, connection strings, and secrets in environment configuration.

Do not place secrets or personal biometric data in source control.

Document privacy and personal data protection considerations applicable to deployment in Indonesia.

# 23. REQUIRED AUTOMATED TESTS

Implement automated tests for:

## Image Processing
- Image decoding.
- Face detection.
- Image cropping.
- Grayscale conversion.
- Resizing.
- HOG feature extraction.
- HOG dimensionality.
- Invalid image handling.

## Machine Learning
- KNN initialization.
- Euclidean distance.
- Known-identity recognition.
- Unknown-face rejection.
- Threshold evaluation.
- PSO parameter constraints.
- PSO reproducibility.
- Model saving and loading.
- Feature-version consistency.

## Ticketing
- Successful registration.
- Duplicate registration rejection.
- Capacity enforcement.
- Successful enrollment.
- QR ticket generation.
- Invalid QR rejection.
- Used-ticket rejection.
- Correct-owner verification.
- Wrong-owner rejection.
- Expired session rejection.
- Single-use ticket protection.
- Concurrent scan protection.

## Frontend
- Login flow.
- Event registration.
- Camera permission states.
- Enrollment progress.
- QR scanner response.
- Verification feedback.
- Ticket status updates.

## End-to-End
- Register → enroll → receive ticket → QR scan → face match → access granted.
- Valid QR → wrong face → access denied.
- Previously used QR → access denied.
- Unknown face → access denied.
- Camera failure → appropriate error.
- Duplicate concurrent check-in → only one success.

Synthetic test fixtures are permitted for software logic tests, but actual recognition performance must be evaluated separately using authorized real datasets.

# 24. DOCUMENTATION

Generate complete documentation in Markdown.

Required documents:

- README.md.
- Architecture Overview.
- System Flowchart.
- Registration Flowchart.
- Facial Enrollment Flowchart.
- Image Processing Flowchart.
- HOG Flowchart.
- KNN Flowchart.
- PSO Flowchart.
- Ticket Verification Flowchart.
- Entity Relationship Diagram.
- Database Design.
- API Documentation.
- Machine Learning Methodology.
- Experimental Protocol.
- Model Comparison.
- Testing Report.
- Known Limitations.
- Deployment Guide.

Use Mermaid diagrams when useful.

Documentation should describe the actual implementation.

# 25. IMPLEMENTATION ROADMAP

Implement in the following order.

## PHASE 1 — PROJECT FOUNDATION

Tasks:

- Inspect repository.
- Create project structure.
- Configure Python environment.
- Initialize FastAPI.
- Initialize Jinja2 templates.
- Configure static HTML, CSS, JavaScript.
- Configure PostgreSQL.
- Implement migrations.
- Implement authentication.
- Implement role authorization.

Deliverable:

A running native-HTML website connected to FastAPI and PostgreSQL.

## PHASE 2 — IMAGE PROCESSING

Tasks:

- Implement image acquisition.
- Implement face detection.
- Implement cropping.
- Implement resizing.
- Implement grayscale conversion.
- Implement HOG.
- Implement feature validation.
- Build image-processing visualization.
- Write unit tests.

Deliverable:

A working, testable face image-processing pipeline.

## PHASE 3 — MACHINE LEARNING

Tasks:

- Implement labeled face dataset handling.
- Implement KNN.
- Implement Euclidean distance.
- Implement recognition threshold.
- Implement unknown-face rejection.
- Implement PSO.
- Implement baseline comparison.
- Implement evaluation scripts.
- Generate plots from actual available data.

Deliverable:

A reproducible HOG-KNN-PSO recognition pipeline.

## PHASE 4 — EVENT AND ENROLLMENT

Tasks:

- Implement event pages.
- Implement registration.
- Implement enrollment UI.
- Implement browser camera capture.
- Integrate preprocessing.
- Store identity features.
- Implement enrollment completion.

Deliverable:

A participant can register and enroll their face.

## PHASE 5 — TICKETING

Tasks:

- Implement unique ticket generation.
- Generate QR Code.
- Display digital tickets.
- Implement ticket status.
- Implement QR validation.
- Implement operator scanner.
- Implement temporary verification sessions.

Deliverable:

A functional ticketing workflow.

## PHASE 6 — FACIAL VERIFICATION

Tasks:

- Capture face at entrance.
- Run preprocessing.
- Extract HOG features.
- Predict KNN identity.
- Verify claimed ticket owner.
- Apply recognition threshold.
- Handle unknown faces.
- Implement atomic single-use check-in.

Deliverable:

QR and face-based venue authorization.

## PHASE 7 — ADMIN AND CV LAB

Tasks:

- Implement admin dashboard.
- Implement operator management.
- Implement event monitoring.
- Implement check-in analytics.
- Implement Computer Vision Lab.
- Display actual ML evaluation results.

Deliverable:

Administrative functionality and academic visualization.

## PHASE 8 — TESTING AND FINALIZATION

Tasks:

- Run unit tests.
- Run integration tests.
- Run end-to-end tests.
- Fix implementation errors.
- Validate authorization.
- Validate concurrency protection.
- Verify frontend-backend integration.
- Complete documentation.
- Provide installation instructions.

Deliverable:

A tested and documented application with clearly stated empirical limitations.

# 26. LOCAL DEVELOPMENT

Provide a working local development setup.

Required capabilities:

- Install Python dependencies.
- Configure PostgreSQL.
- Initialize database.
- Run migrations.
- Create initial administrator.
- Start FastAPI server.
- Open website locally.
- Run test suite.
- Run ML training scripts.
- Run evaluation scripts.

Support Windows development and PowerShell commands in the README.

A typical development entry point may be:

    python -m uvicorn app.main:app --reload

The exact command must match the implemented project.

Provide a complete `.env.example`.

Do not require paid services for local development.

# 27. ACCEPTANCE CRITERIA

The implementation can be considered functionally complete only when:

- Users can register and log in.
- Administrators can create events.
- Participants can register for available events.
- Facial enrollment captures actual images.
- The backend preprocesses real facial images.
- HOG extracts real numerical descriptors.
- KNN can classify enrolled identities.
- Unknown-face rejection is implemented.
- PSO can optimize defined KNN parameters.
- Experiment scripts can compare KNN and PSO-KNN.
- Successful enrollment issues a QR ticket.
- QR scanning validates the actual stored ticket.
- Facial verification checks the ticket's owner.
- Incorrect faces are rejected.
- Used tickets cannot be reused.
- Ticket consumption is atomic.
- Operator access is role restricted.
- CV Lab displays actual processing results.
- Automated software tests pass.
- Installation instructions are accurate.
- Scientific assumptions and limitations are documented.

Actual facial recognition performance must not be marked as validated until appropriate real evaluation data has been tested.

# 28. STRICT CODING AGENT INSTRUCTIONS

Follow these instructions throughout implementation:

1. Do not use React or any frontend framework.
2. Do not introduce an unnecessary Node.js build process.
3. Use native HTML, CSS, and Vanilla JavaScript.
4. Use Jinja2 for reusable page templates.
5. Use FastAPI as the primary application backend.
6. Implement the machine learning pipeline in Python.
7. Use HOG-KNN-PSO as the core methodology.
8. Keep computer vision modules independent from HTTP routes.
9. Keep model training separate from production inference.
10. Do not fabricate facial recognition accuracy.
11. Do not hardcode successful recognition.
12. Do not fake database records in production workflows.
13. Do not bypass face verification after QR validation.
14. Do not use public folders for biometric image storage.
15. Do not rely on frontend-only authorization.
16. Avoid overengineering and unnecessary dependencies.
17. Use reusable CSS and JavaScript modules.
18. Ensure the website remains responsive and accessible.
19. Run tests after significant implementation changes.
20. Fix identified errors before claiming completion.
21. Clearly distinguish operational functionality from scientifically validated recognition performance.
22. If real facial datasets are missing, complete the application architecture, CV pipeline, training scripts, and test fixtures without inventing evaluation results.
23. Do not claim anti-spoofing resistance without dedicated testing.
24. Provide accurate progress and completion summaries.
25. Preserve a functioning repository throughout development.

# 29. WORK EXECUTION STRATEGY

Begin by inspecting all existing project files.

If the project directory is empty, initialize the project according to the specified architecture.

Create a concise implementation plan and then begin writing actual code.

Work through the implementation phases sequentially.

For each phase:

1. Identify required modules.
2. Implement functional code.
3. Integrate dependencies.
4. Execute available tests.
5. Fix errors.
6. Document completed functionality.
7. Proceed to the next phase.

Use reasonable engineering defaults when requirements do not specify a minor implementation detail.

Avoid unnecessary clarification requests when the project can proceed safely using the documented requirements.

If a task requires unavailable real biometric images, external credentials, or user consent, do not fabricate the missing input. Complete all independent development work and clearly report the blocker.

# 30. FINAL PROJECT GOAL

Deliver a complete Smart Event Ticketing System with:

**Frontend:** Native HTML5 + CSS3 + Vanilla JavaScript.

**Backend:** FastAPI + Jinja2.

**Database:** PostgreSQL.

**Computer Vision:** OpenCV + HOG.

**Machine Learning:** KNN + PSO.

**Authentication:** Secure QR Code + Facial Verification.

**Ticket Policy:** Single Successful Use.

**Academic Output:** Reproducible experiments, image-processing visualizations, evaluation metrics, and algorithm comparison.

The application should demonstrate the complete journey:

User Registration → Event Registration → Facial Enrollment → HOG Feature Extraction → Identity Registration → QR Ticket Generation → Event Check-in → QR Validation → Live Facial Verification → KNN Identity Matching → Threshold Validation → Atomic Ticket Consumption → Access Granted or Denied.

The main research contribution must remain focused on image processing and facial recognition.

The website is the implementation environment for demonstrating and evaluating those algorithms.

**START IMPLEMENTING THE PROJECT NOW. DO NOT STOP AT PLANNING OR MOCKUP GENERATION.**