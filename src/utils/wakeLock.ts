// Web Screen Wake Lock and Audio utilities

export interface WakeLockManager {
  request: () => Promise<boolean>;
  release: () => Promise<void>;
  isSupported: () => boolean;
  isActive: () => boolean;
}

class ScreenWakeLockService implements WakeLockManager {
  private sentinel: WakeLockSentinel | null = null;
  private onReleaseCallback: (() => void) | null = null;

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'wakeLock' in navigator;
  }

  isActive(): boolean {
    return this.sentinel !== null && !this.sentinel.released;
  }

  setReleaseListener(cb: () => void) {
    this.onReleaseCallback = cb;
  }

  async request(): Promise<boolean> {
    if (!this.isSupported()) {
      return false;
    }

    try {
      this.sentinel = await navigator.wakeLock.request('screen');
      this.sentinel.addEventListener('release', () => {
        this.sentinel = null;
        if (this.onReleaseCallback) {
          this.onReleaseCallback();
        }
      });
      return true;
    } catch (err) {
      console.warn('Wake Lock request failed:', err);
      return false;
    }
  }

  async release(): Promise<void> {
    if (this.sentinel) {
      try {
        await this.sentinel.release();
      } catch (err) {
        console.warn('Error releasing Wake Lock:', err);
      } finally {
        this.sentinel = null;
      }
    }
  }
}

export const wakeLockService = new ScreenWakeLockService();

// Audio synthesizers using Web Audio API for feedback
let audioCtx: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  try {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      audioCtx = new AudioContextClass();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  } catch {
    return null;
  }
}

export function playSignalChime(): void {
  const ctx = getAudioContext();
  if (!ctx) return;
  try {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
    osc.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.08);

    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.1);
  } catch {
    // Audio playback blocked or unsupported
  }
}

export function playWarningBeep(): void {
  const ctx = getAudioContext();
  if (!ctx) return;
  try {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.frequency.setValueAtTime(554.37, ctx.currentTime + 0.15); // C#5

    gain.gain.setValueAtTime(0.12, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } catch {
    // Audio playback blocked or unsupported
  }
}

export function parsePowerDeadline(text: string): number | null {
  const clean = text.trim();
  if (!clean) return null;

  if (clean.includes(':')) {
    const parts = clean.split(':');
    if (parts.length !== 2) return null;
    const hh = parseInt(parts[0], 10);
    const mm = parseInt(parts[1], 10);
    if (isNaN(hh) || isNaN(mm) || hh < 0 || hh >= 24 || mm < 0 || mm >= 60) {
      return null;
    }
    const now = new Date();
    const target = new Date(now);
    target.setHours(hh, mm, 0, 0);
    if (target.getTime() <= now.getTime()) {
      target.setDate(target.getDate() + 1);
    }
    return target.getTime();
  }

  const minutes = parseFloat(clean);
  if (isNaN(minutes) || minutes <= 0) return null;
  return Date.now() + minutes * 60 * 1000;
}
