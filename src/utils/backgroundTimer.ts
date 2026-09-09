// Background-resilient timer using an inline Web Worker.
// Browsers throttle window.setInterval in inactive/minimized tabs,
// but Web Workers run unthrottled in their own thread.
// Gracefully falls back to window.setInterval if Workers are blocked.

export type TimerCallback = () => void;

export class BackgroundHeartbeat {
  private worker: Worker | null = null;
  private fallbackTimerId: number | null = null;
  private onTick: TimerCallback | null = null;

  constructor() {
    this.initWorker();
  }

  private initWorker() {
    if (typeof window === 'undefined' || typeof Worker === 'undefined') {
      return;
    }

    try {
      const code = `
        let timer = null;
        self.onmessage = function(e) {
          if (e.data.action === 'start') {
            if (timer) clearInterval(timer);
            timer = setInterval(function() {
              self.postMessage('tick');
            }, e.data.intervalMs);
          } else if (e.data.action === 'stop') {
            if (timer) {
              clearInterval(timer);
              timer = null;
            }
          }
        };
      `;
      const blob = new Blob([code], { type: 'application/javascript' });
      const workerUrl = URL.createObjectURL(blob);
      this.worker = new Worker(workerUrl);
      this.worker.onmessage = (e) => {
        if (e.data === 'tick' && this.onTick) {
          this.onTick();
        }
      };
    } catch {
      // Fallback to standard window timer if worker creation is blocked
      this.worker = null;
    }
  }

  start(intervalMs: number, callback: TimerCallback) {
    this.stop();
    this.onTick = callback;

    if (this.worker) {
      try {
        this.worker.postMessage({ action: 'start', intervalMs });
        return;
      } catch {
        // Fall through to fallback
      }
    }

    this.fallbackTimerId = window.setInterval(() => {
      if (this.onTick) {
        this.onTick();
      }
    }, intervalMs);
  }

  stop() {
    if (this.worker) {
      try {
        this.worker.postMessage({ action: 'stop' });
      } catch {
        // Ignore
      }
    }
    if (this.fallbackTimerId !== null) {
      window.clearInterval(this.fallbackTimerId);
      this.fallbackTimerId = null;
    }
    this.onTick = null;
  }

  destroy() {
    this.stop();
    if (this.worker) {
      try {
        this.worker.terminate();
      } catch {
        // Ignore
      }
      this.worker = null;
    }
  }
}
