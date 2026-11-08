/**
 * Facial Enrollment Interactive Controller
 */
const POSES = [
  { id: 'frontal_1', label: 'Frontal Neutral Face', instruction: 'Look directly at the camera with a neutral expression.' },
  { id: 'slight_left', label: 'Slight Left Turn', instruction: 'Gently turn your head slightly to your left.' },
  { id: 'slight_right', label: 'Slight Right Turn', instruction: 'Gently turn your head slightly to your right.' },
  { id: 'angle_left', label: 'Moderate Left Angle', instruction: 'Turn a bit more towards your left.' },
  { id: 'angle_right', label: 'Moderate Right Angle', instruction: 'Turn a bit more towards your right.' },
  { id: 'slight_up', label: 'Slight Tilt Up', instruction: 'Tilt your chin slightly upwards.' },
  { id: 'slight_down', label: 'Slight Tilt Down', instruction: 'Tilt your head slightly downwards.' },
  { id: 'expression', label: 'Mild Expression', instruction: 'Smile naturally or show a pleasant expression.' },
  { id: 'frontal_2', label: 'Final Frontal Capture', instruction: 'Look straight at the camera one more time.' }
];

class EnrollmentManager {
  constructor(videoEl, statusEl, progressEl, previewContainerEl, btnCapture, btnStart) {
    this.videoEl = videoEl;
    this.statusEl = statusEl;
    this.progressEl = progressEl;
    this.previewContainerEl = previewContainerEl;
    this.btnCapture = btnCapture;
    this.btnStart = btnStart;

    this.camera = new CameraController(videoEl);
    this.currentStep = 0;
    this.capturedSamples = [];

    this.initEvents();
  }

  initEvents() {
    this.btnStart?.addEventListener('click', () => this.startCamera());
    this.btnCapture?.addEventListener('click', () => this.captureSample());
    const fileInput = document.getElementById('enroll-file-input');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
    }
  }

  async startCamera() {
    try {
      this.statusEl.textContent = 'Requesting camera access...';
      await this.camera.start();
      this.btnStart.style.display = 'none';
      this.btnCapture.disabled = false;
      this.updateStepPrompt();
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    }
  }

  updateStepPrompt() {
    if (this.currentStep < POSES.length) {
      const pose = POSES[this.currentStep];
      this.statusEl.innerHTML = `<strong>Sample ${this.currentStep + 1} of ${POSES.length}: ${pose.label}</strong><br><small>${pose.instruction}</small>`;
      const pct = Math.round((this.currentStep / POSES.length) * 100);
      if (this.progressEl) {
        this.progressEl.style.width = `${pct}%`;
        this.progressEl.textContent = `${pct}%`;
      }
    } else {
      this.statusEl.innerHTML = `<strong>All 9 samples captured!</strong> Please review and confirm your biometric consent below.`;
      if (this.progressEl) {
        this.progressEl.style.width = '100%';
        this.progressEl.textContent = '100%';
      }
      this.btnCapture.disabled = true;
      const consentSec = document.getElementById('consent-section');
      if (consentSec) {
        consentSec.style.display = 'block';
      }
    }
  }

  handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file || this.currentStep >= POSES.length) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      await this.processSampleData(b64);
      event.target.value = '';
    };
    reader.readAsDataURL(file);
  }

  async processSampleData(frameData) {
    this.btnCapture.disabled = true;
    this.statusEl.textContent = 'Validating facial quality & extracting HOG descriptors...';

    try {
      const currentPose = POSES[this.currentStep];
      const res = await API.post('/api/enrollment/sample', {
        image_base64: frameData,
        pose_label: currentPose.id
      });

      if (res.success) {
        this.capturedSamples.push({
          pose: currentPose,
          thumb: frameData,
          id: res.sample_id
        });

        this.addThumbnail(frameData, currentPose.label);
        this.currentStep++;
        this.updateStepPrompt();
      } else {
        this.statusEl.innerHTML = `<span style="color: var(--danger);">Sample rejected: ${res.message}</span><br><small>Please adjust your position and try again.</small>`;
      }
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    } finally {
      if (this.currentStep < POSES.length && this.camera.isStreaming) {
        this.btnCapture.disabled = false;
      }
    }
  }

  async captureSample() {
    if (this.currentStep >= POSES.length) return;
    const frameData = this.camera.captureFrame();
    await this.processSampleData(frameData);
  }

  addThumbnail(imgSrc, label) {
    const noMsg = document.getElementById('no-samples-msg');
    if (noMsg) noMsg.style.display = 'none';

    const thumb = document.createElement('div');
    thumb.className = 'sample-thumb-card';
    thumb.innerHTML = `
      <img src="${imgSrc}" alt="${label}" style="width: 70px; height: 70px; object-fit: cover; border-radius: var(--radius-sm); border: 1px solid var(--border);" />
      <span style="font-size: 0.7rem; color: var(--text-muted); display: block; text-align: center; margin-top: 4px;">${label}</span>
    `;
    this.previewContainerEl.appendChild(thumb);
  }
}
