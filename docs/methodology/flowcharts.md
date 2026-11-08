# System Workflow & Algorithm Flowcharts

---

## 1. Participant Registration & 9-Pose Facial Enrollment

```mermaid
flowchart TD
    Start([User Visits Website]) --> Reg[Register / Login Account]
    Reg --> Browse[Select Upcoming Event]
    Browse --> SubmitReg[Submit Event Registration]
    SubmitReg --> CheckConsent{Biometric Consent Granted?}
    CheckConsent -- No --> Stop([Registration Blocked])
    CheckConsent -- Yes --> OpenCam[Initialize Webcam Stream]
    OpenCam --> PosePrompt[Display Pose Instruction 1 to 9]
    PosePrompt --> Capture[Capture Frame on HTML5 Canvas]
    Capture --> QC{OpenCV Quality Check:<br/>1 Face? Centered? Sharp? Good Light?}
    QC -- Failed --> Adjust[Display Feedback & Retake Sample]
    Adjust --> Capture
    QC -- Passed --> Crop[Crop Face ROI & Resize 128x128]
    Crop --> Gray[Grayscale: 0.2989R + 0.5870G + 0.1140B]
    Gray --> HOG[Extract 8,100-dim HOG Descriptor]
    HOG --> SaveSample[Store Private Image & Feature Vector]
    SaveSample --> NextPose{All 9 Poses Captured?}
    NextPose -- No --> PosePrompt
    NextPose -- Yes --> Complete[Confirm Enrollment in Database]
    Complete --> IssueTicket[Generate Unique Cryptographic QR Token]
    IssueTicket --> SaveTicket[Store SHA-256 Hash as ACTIVE Ticket]
    SaveTicket --> EndReg([Participant Receives Digital QR Ticket])
```

---

## 2. Venue Entrance Check-In & Two-Factor Authentication

```mermaid
flowchart TD
    Arr([Participant Arrives at Venue]) --> OpOpen[Operator Launches Venue Scanner]
    OpOpen --> ScanQR[Scan Digital QR Ticket]
    ScanQR --> HashToken[Compute SHA-256 Hash of QR Token]
    HashToken --> QueryDB{Ticket Exists in Database?}
    QueryDB -- No --> DenyInvalid[ACCESS DENIED: Invalid QR Code]
    QueryDB -- Yes --> CheckStatus{Ticket Status?}
    CheckStatus -- USED --> DenyUsed[ACCESS DENIED: Ticket Already Consumed]
    CheckStatus -- CANCELLED --> DenyCancel[ACCESS DENIED: Ticket Cancelled]
    CheckStatus -- ACTIVE --> CreateSess[Create 3-Minute Verification Session]
    CreateSess --> FaceCam[Participant Faces Entrance Camera]
    FaceCam --> CapFace[Capture Entrance Facial Frame]
    CapFace --> DetectFace{Exactly 1 Face Detected?}
    DetectFace -- No --> RetryFace[ACCESS DENIED: Bad Capture / Reposition Face]
    DetectFace -- Yes --> ProcHOG[128x128 Crop & Compute 8,100-dim HOG]
    ProcHOG --> KNNMatch[KNN Euclidean Distance vs Ticket Owner Gallery]
    KNNMatch --> MatchOwner{Predicted ID == Ticket Owner?}
    MatchOwner -- No --> DenyMismatch[ACCESS DENIED: Face Mismatch]
    MatchOwner -- Yes --> ThreshCheck{Distance <= Calibrated Threshold?}
    ThreshCheck -- No --> DenyThresh[ACCESS DENIED: Exceeds Recognition Threshold]
    ThreshCheck -- Yes --> AtomicUpdate[ATOMIC UPDATE: SET status='USED', used_at=now]
    AtomicUpdate --> CollideCheck{Update Succeeded?}
    CollideCheck -- No / Rowcount=0 --> DenyRace[ACCESS DENIED: Concurrent Entry Attempt]
    CollideCheck -- Yes --> Grant[ACCESS GRANTED: Turnstile Opens & Welcome]
```

---

## 3. Computer Vision & HOG Descriptor Flowchart

```mermaid
flowchart TD
    Input[Input BGR Frame from Camera] --> Detect[OpenCV Haar Cascade Face Detection]
    Detect --> Box[Extract Bounding Box with 10% Margin]
    Box --> Crop[Crop Face Region of Interest]
    Crop --> Resize[Resize to 128 x 128 pixels]
    Resize --> Gray[Grayscale Conversion BT.601]
    Gray --> HistEq[Histogram Equalization]
    HistEq --> Grad[Apply Centered Derivative Kernels: dx, dy]
    Grad --> MagOri[Compute Magnitude M and Orientation Theta 0-180 deg]
    MagOri --> GridCells[Partition into 16 x 16 Cells of 8x8 pixels]
    GridCells --> CellHist[Accumulate 9-bin Histograms per Cell]
    CellHist --> Blocks[Group into 15 x 15 Overlapping 2x2 Cell Blocks]
    Blocks --> L2Hys[Apply L2-Hys Block Normalization]
    L2Hys --> Concat[Concatenate 225 Blocks x 36 Values]
    Concat --> Vector[Final 8,100-Dimensional HOG Feature Vector]
```

---

## 4. Particle Swarm Optimization (PSO) Flowchart

```mermaid
flowchart TD
    StartPSO([Initialize PSO Parameter Optimizer]) --> SetBounds[Set Parameter Bounds: k in 1-9, Threshold in 0.45-0.75]
    SetBounds --> InitSwarm[Initialize N Particles with Random Positions & Velocities]
    InitSwarm --> EvalFit[Evaluate Validation Fitness for each Particle]
    EvalFit --> CalcFit[Fitness = 0.70*Acc + 0.30*Rejection - 1.50*FAR]
    CalcFit --> UpdatePbest[Update Personal Best Position & Fitness]
    UpdatePbest --> UpdateGbest[Update Global Best Swarm Position]
    UpdateGbest --> TermCheck{Stopping Criteria Met? Iteration Limit?}
    TermCheck -- No --> CalcVelocity[Compute Velocity: w*v + c1*r1*pbest_diff + c2*r2*gbest_diff]
    CalcVelocity --> UpdatePos[Update Position: x = x + v]
    UpdatePos --> Clip[Clip Parameters to Search Bounds]
    Clip --> EvalFit
    TermCheck -- Yes --> SaveOpt[Save Optimized k and Distance Threshold]
    SaveOpt --> Deploy[Deploy Active Model Version to Inference Engine]
```

