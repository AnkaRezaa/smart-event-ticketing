/**
 * Computer Vision & Machine Learning Laboratory Client Controller
 */
class CVLabController {
  constructor() {
    this.videoEl = document.getElementById('lab-camera');
    this.camera = new CameraController(this.videoEl);

    this.btnStartCamera = document.getElementById('btn-lab-camera-start');
    this.btnCapture = document.getElementById('btn-lab-capture');
    this.fileInput = document.getElementById('lab-file-input');
    this.statusEl = document.getElementById('lab-status');

    this.resultsContainer = document.getElementById('lab-results');

    this.initEvents();
  }

  initEvents() {
    this.btnStartCamera?.addEventListener('click', () => this.startCamera());
    this.btnCapture?.addEventListener('click', () => this.analyzeCameraFrame());
    this.fileInput?.addEventListener('change', (e) => this.handleFileUpload(e));
  }

  async startCamera() {
    try {
      this.statusEl.textContent = 'Starting webcam stream...';
      await this.camera.start();
      this.btnStartCamera.style.display = 'none';
      this.btnCapture.disabled = false;
      this.statusEl.textContent = 'Camera active. Frame your face and click "Analyze Frame".';
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    }
  }

  async analyzeCameraFrame() {
    try {
      const frameData = this.camera.captureFrame();
      await this.runAnalysis(frameData);
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    }
  }

  handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      await this.runAnalysis(b64);
    };
    reader.readAsDataURL(file);
  }

  async runAnalysis(imageData) {
    this.statusEl.textContent = 'Processing frame through OpenCV & HOG extraction pipeline...';
    this.resultsContainer.style.display = 'none';

    try {
      const res = await API.post('/api/cv-lab/inspect', { image_base64: imageData });

      if (!res.success) {
        this.statusEl.innerHTML = `<span style="color: var(--danger);">Inspection failed: ${res.message}</span>`;
        return;
      }

      this.statusEl.innerHTML = `<span style="color: var(--success);">✓ Pipeline executed successfully in ${res.latency_ms.toFixed(1)} ms</span>`;
      this.renderVisualizations(res);
      this.resultsContainer.style.display = 'block';
    } catch (err) {
      this.statusEl.innerHTML = `<span style="color: var(--danger);">${err.message}</span>`;
    }
  }

  renderVisualizations(data) {
    const v = data.visualizations;

    document.getElementById('vis-annotated').src = v.annotated_image;
    document.getElementById('vis-roi').src = v.roi_image;
    document.getElementById('vis-gray').src = v.gray_image;
    document.getElementById('vis-equalized').src = v.equalized_image;

    document.getElementById('vis-gx').src = v.gx_image;
    document.getElementById('vis-gy').src = v.gy_image;
    document.getElementById('vis-mag').src = v.magnitude_image;
    document.getElementById('vis-ori').src = v.orientation_image;

    if (v.hog_image) {
      document.getElementById('vis-hog').src = v.hog_image;
    }

    // Feature summary
    const fs = v.feature_summary;
    document.getElementById('vis-dim').textContent = `${fs.dimension} numerical features`;
    document.getElementById('vis-stats').innerHTML = `
      Min: <code>${fs.min.toFixed(4)}</code> | 
      Max: <code>${fs.max.toFixed(4)}</code> | 
      Mean: <code>${fs.mean.toFixed(4)}</code> | 
      Std: <code>${fs.std.toFixed(4)}</code> | 
      Sparsity: <code>${fs.sparsity_zeros_pct.toFixed(1)}% zeros</code>
    `;
    document.getElementById('vis-first-values').textContent = fs.first_20_values.join(', ') + ' ...';

    // ML classification prediction if available
    const ml = data.ml_decision;
    if (ml) {
      document.getElementById('ml-pred-user').textContent = ml.predicted_label || 'None (Gallery Empty)';
      document.getElementById('ml-pred-dist').textContent = ml.min_distance !== undefined ? ml.min_distance.toFixed(4) : 'N/A';
      document.getElementById('ml-pred-thresh').textContent = ml.active_threshold;
      document.getElementById('ml-pred-verdict').innerHTML = ml.is_within_threshold
        ? '<span class="badge badge-success">Recognized Identity</span>'
        : '<span class="badge badge-danger">UNKNOWN (Rejected by threshold)</span>';
    }
  }
}

