// Safe cross-platform Battery Guard
// Supported in Chrome / Edge / Opera on Windows & macOS.
// Gracefully degrades on Safari and Firefox without throwing any errors.

export interface BatteryState {
  supported: boolean;
  charging: boolean | null;
  level: number | null; // 0 to 100
}

interface BatteryManagerAPI extends EventTarget {
  charging: boolean;
  chargingTime: number;
  dischargingTime: number;
  level: number;
  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void;
  removeEventListener(type: string, listener: EventListenerOrEventListenerObject): void;
}

type BatteryChangeCallback = (state: BatteryState) => void;

class BatteryGuardService {
  private listeners: BatteryChangeCallback[] = [];
  private currentState: BatteryState = {
    supported: false,
    charging: null,
    level: null,
  };
  private initialized = false;

  async init(): Promise<BatteryState> {
    if (this.initialized) {
      return this.currentState;
    }
    this.initialized = true;

    if (
      typeof window === 'undefined' ||
      typeof navigator === 'undefined' ||
      !('getBattery' in navigator)
    ) {
      this.currentState = { supported: false, charging: null, level: null };
      return this.currentState;
    }

    try {
      const getBatteryFn = (navigator as unknown as { getBattery: () => Promise<BatteryManagerAPI> }).getBattery;
      if (typeof getBatteryFn !== 'function') {
        this.currentState = { supported: false, charging: null, level: null };
        return this.currentState;
      }

      const battery = await getBatteryFn.call(navigator);

      const updateState = () => {
        this.currentState = {
          supported: true,
          charging: battery.charging,
          level: Math.round(battery.level * 100),
        };
        this.notify();
      };

      battery.addEventListener('levelchange', updateState);
      battery.addEventListener('chargingchange', updateState);

      updateState();
      return this.currentState;
    } catch {
      this.currentState = { supported: false, charging: null, level: null };
      return this.currentState;
    }
  }

  getState(): BatteryState {
    return this.currentState;
  }

  subscribe(callback: BatteryChangeCallback): () => void {
    this.listeners.push(callback);
    callback(this.currentState);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }

  private notify() {
    for (const listener of this.listeners) {
      listener(this.currentState);
    }
  }
}

export const batteryGuard = new BatteryGuardService();
