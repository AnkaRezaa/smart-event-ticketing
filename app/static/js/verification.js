/**
 * Venue Check-in & Operator 2-Stage Verification Logic
 */
class VenueCheckinController {
  constructor() {
    this.videoEl = document.getElementById('operator-camera');
    this.camera = new CameraController(this.videoEl);
    this.qrScanner = null;
    this.currentSession = null;

    this.qrStepCard = document.getElementById('step-qr-card');
    this.faceStepCard = document.getElementById('step-face-card');
    this.resultCard = document.getElementById('result-card');

    this.statusEl = document.getElementById('checkin-status');
    this.btnStartCamera = document.getElementById('btn-start-camera');
    this.btnCaptureFace = document.getElementById('btn-verify-face');
    this.btnManualQR = document.getElementById('btn-manual-qr');
    this.inputManualQR = document.getElementById('manual-qr-token');
    this.inputFileFace = document.getElementById('face-file-input');
    this.btnNextPerson = document.getElementById('btn-next-person');

    this.initEvents();
  }

  initEvents() {
    this.btnStartCamera?.addEventListener('click', () => this.startWorkflow());
    this.btnManualQR?.addEventListener('click', () => this.handleManualQR());
    this.btnCaptureFace?.addEventListener('click', () => this.verifyFace());
    this.inputFileFace?.addEventListener('change', (e) => this.handleFaceFileUpload(e));
    this.btnNextPerson?.addEventListener('click', () => this.resetWorkflow());
  }

  handleFaceFileUpload(event) {
    const file = event.target.files[0];
    if (!file || !this.currentSession) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      this.statusEl.textContent = 'Analyzing facial image with HOG, KNN, & PSO threshold...';
      try {
        const res = await API.post('/api/checkin/verify-face', {
          session_id: this.currentSession.session_id,
          image_base64: b64
        });
        this.showVerdict(res.authorized, res.message, res);
      } catch (err) {
        this.showVerdict(false, err.message, {});
      }
    };
    reader.readAsDataURL(file);
  }

  async startWorkflow() {
    try {
      this.statusEl.textContent = 'Activating venue scanner camera...';
      await this.camera.start();
      this.btnStartCamera.style.display = 'none';

      // Start QR scanner on camera
      this.qrScanner = new QRScanner(this.videoEl, (token) => this.onQRDetected(token));
      this.qrScanner.start();
      this.statusEl.innerHTML = '<strong>Point camera at participant QR ticket</strong>';
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    }
  }

  async handleManualQR() {
    const token = this.inputManualQR.value.trim();
    if (!token) {
      alert('Please enter or scan a valid QR ticket token');
      return;
    }
    await this.onQRDetected(token);
  }

  async onQRDetected(rawToken) {
    if (this.qrScanner) {
      this.qrScanner.stop();
    }

    this.statusEl.textContent = 'Validating ticket QR Code against registry...';

    try {
      const res = await API.post('/api/checkin/validate-qr', { qr_token: rawToken });

      if (!res.valid) {
        this.showVerdict(false, res.message, { failure_code: res.failure_code });
        return;
      }

      // QR is valid! Transition to Stage 2: Face Verification
      this.currentSession = res;
      this.statusEl.innerHTML = `
        <span style="color: var(--success);">✓ Ticket Valid:</span> <strong>${res.owner_name}</strong> (${res.event_title})<br>
        <span style="color: var(--primary);">Stage 2: Align participant's face with the camera.</span>
      `;

      this.qrStepCard.style.display = 'none';
      this.faceStepCard.style.display = 'block';
      this.btnCaptureFace.disabled = false;
    } catch (err) {
      this.showVerdict(false, err.message, {});
    }
  }

  async verifyFace() {
    if (!this.currentSession) return;

    this.btnCaptureFace.disabled = true;
    this.statusEl.textContent = 'Analyzing facial image with HOG, KNN, & PSO threshold...';

    try {
      const faceData = this.camera.captureFrame();
      const res = await API.post('/api/checkin/verify-face', {
        session_id: this.currentSession.session_id,
        image_base64: faceData
      });

      this.showVerdict(res.authorized, res.message, res);
    } catch (err) {
      this.showVerdict(false, err.message, {});
    }
  }

  showVerdict(isGranted, message, details) {
    this.qrStepCard.style.display = 'none';
    this.faceStepCard.style.display = 'none';
    this.resultCard.style.display = 'block';

    const banner = document.getElementById('verdict-banner');
    const msgEl = document.getElementById('verdict-message');
    const metaEl = document.getElementById('verdict-details');

    if (isGranted) {
      banner.className = 'verdict-banner verdict-granted';
      banner.innerHTML = `<h1>ACCESS GRANTED</h1><p>Owner: <strong>${details.owner_name || 'Verified Ticket Holder'}</strong></p>`;
      msgEl.innerHTML = `<span style="color: var(--success); font-weight: 600;">${message}</span>`;
    } else {
      banner.className = 'verdict-banner verdict-denied';
      banner.innerHTML = `<h1>ACCESS DENIED</h1><p>Verification Check Failed</p>`;
      msgEl.innerHTML = `<span style="color: var(--danger); font-weight: 600;">${message}</span>`;
    }

    let detailHtml = '';
    if (details.owner_distance !== undefined) {
      detailHtml += `<div>Euclidean Distance: <code>${details.owner_distance}</code> (Threshold: <code>${details.threshold}</code>)</div>`;
    }
    if (details.confidence !== undefined) {
      detailHtml += `<div>Confidence Score: <code>${(details.confidence * 100).toFixed(1)}%</code></div>`;
    }
    metaEl.innerHTML = detailHtml;
  }

  resetWorkflow() {
    this.currentSession = null;
    this.resultCard.style.display = 'none';
    this.faceStepCard.style.display = 'none';
    this.qrStepCard.style.display = 'block';
    if (this.inputManualQR) this.inputManualQR.value = '';

    if (this.camera.isStreaming && this.qrScanner) {
      this.qrScanner.start();
      this.statusEl.innerHTML = '<strong>Ready for next participant: Point camera at QR ticket</strong>';
    } else {
      this.btnStartCamera.style.display = 'inline-flex';
      this.statusEl.textContent = 'Click "Activate Scanner" to begin check-in.';
    }
  }
}

