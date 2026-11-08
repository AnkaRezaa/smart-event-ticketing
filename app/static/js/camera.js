/**
 * Camera Handler using HTML5 MediaDevices & Canvas API
 */
class CameraController {
  constructor(videoElement, canvasElement = null) {
    this.video = videoElement;
    this.canvas = canvasElement || document.createElement('canvas');
    this.stream = null;
    this.isStreaming = false;
  }

  async start(constraints = { video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' } }) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera access is not supported by this browser or protocol requires HTTPS / localhost.');
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;
      await this.video.play();
      this.isStreaming = true;
      return true;
    } catch (err) {
      this.isStreaming = false;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        throw new Error('Camera permission denied. Please allow camera access in your browser.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        throw new Error('No webcam found on this device.');
      } else {
        throw new Error(`Camera error: ${err.message}`);
      }
    }
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    this.isStreaming = false;
    if (this.video) {
      this.video.srcObject = null;
    }
  }

  captureFrame(format = 'image/jpeg', quality = 0.92) {
    if (!this.isStreaming || !this.video.videoWidth) {
      throw new Error('Camera stream is not active');
    }

    this.canvas.width = this.video.videoWidth;
    this.canvas.height = this.video.videoHeight;
    const ctx = this.canvas.getContext('2d');

    // Draw un-mirrored for accurate computer vision processing
    ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);

    return this.canvas.toDataURL(format, quality);
  }
}

