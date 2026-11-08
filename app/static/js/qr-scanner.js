/**
 * QR Code Scanner with BarcodeDetector and fallback
 */
class QRScanner {
  constructor(videoElement, onDetectedCallback) {
    this.video = videoElement;
    this.onDetected = onDetectedCallback;
    this.isScanning = false;
    this.detector = null;
    this.animationId = null;

    if ('BarcodeDetector' in window) {
      this.detector = new BarcodeDetector({ formats: ['qr_code'] });
    }
  }

  async start() {
    this.isScanning = true;
    this.scanLoop();
  }

  stop() {
    this.isScanning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  async scanLoop() {
    if (!this.isScanning) return;

    if (this.video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA) {
      if (this.detector) {
        try {
          const barcodes = await this.detector.detect(this.video);
          if (barcodes.length > 0) {
            const rawValue = barcodes[0].rawValue;
            this.stop();
            this.onDetected(rawValue);
            return;
          }
        } catch (e) {
          // ignore detection frame errors
        }
      }
    }

    this.animationId = requestAnimationFrame(() => this.scanLoop());
  }
}

