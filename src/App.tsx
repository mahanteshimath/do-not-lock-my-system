import { useState, useEffect, useRef, useCallback } from 'react';
import {
  wakeLockService,
  playSignalChime,
  parsePowerDeadline,
} from './utils/wakeLock';
import { BackgroundHeartbeat } from './utils/backgroundTimer';
import { batteryGuard, BatteryState } from './utils/battery';
import { PowerWarningModal } from './components/PowerWarningModal';
import { DesktopScriptModal } from './components/DesktopScriptModal';
import { LaunchKitModal } from './components/LaunchKitModal';
import {
  Volume2,
  VolumeX,
  Terminal,
  MonitorUp,
  Power,
  Sparkles,
  Battery,
  BatteryCharging,
  BatteryWarning,
  ShieldCheck,
} from 'lucide-react';

interface PresetConfig {
  id: string;
  name: string;
  emoji: string;
  interval: string;
  action: string;
  time: string;
}

const PRESETS: PresetConfig[] = [
  { id: 'continuous', name: 'Continuous', emoji: '♾️', interval: '30', action: 'Off', time: '' },
  { id: 'agent', name: '30m Agent', emoji: '⚡', interval: '30', action: 'Sleep', time: '30' },
  { id: 'model', name: '2h Model Run', emoji: '📦', interval: '30', action: 'Sleep', time: '120' },
  { id: 'overnight', name: '6h Overnight', emoji: '🌙', interval: '30', action: 'Shutdown', time: '360' },
];

export default function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [intervalSec, setIntervalSec] = useState('30');
  const [signalsCount, setSignalsCount] = useState(0);
  const [lastSignalTime, setLastSignalTime] = useState<string | null>(null);
  const [pulseState, setPulseState] = useState(false);

  // Power action options
  const [powerAction, setPowerAction] = useState('Off');
  const [powerTime, setPowerTime] = useState('');
  const [powerDeadline, setPowerDeadline] = useState<number | null>(null);
  const [showPowerWarning, setShowPowerWarning] = useState(false);
  const [executedPowerAction, setExecutedPowerAction] = useState<string | null>(null);
  const [batteryStopNotice, setBatteryStopNotice] = useState<string | null>(null);

  // Checkbox states
  const [lidClosedStayAwake, setLidClosedStayAwake] = useState(true);
  const [startAtLogin, setStartAtLogin] = useState(false);

  // Audio chime & modals
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [showDesktopModal, setShowDesktopModal] = useState(false);
  const [showLaunchKitModal, setShowLaunchKitModal] = useState(false);

  // Wake lock & Battery status
  const [wakeLockActive, setWakeLockActive] = useState(false);
  const [batteryState, setBatteryState] = useState<BatteryState>({
    supported: false,
    charging: null,
    level: null,
  });

  // Selected preset tracking
  const [selectedPresetId, setSelectedPresetId] = useState<string>('continuous');

  // Refs for timers and workers
  const heartbeatWorkerRef = useRef<BackgroundHeartbeat | null>(null);
  const pulseTimerRef = useRef<number | null>(null);
  const powerCountdownRef = useRef<number | null>(null);

  // Initialize Battery Guard & Wake Lock listeners
  useEffect(() => {
    wakeLockService.setReleaseListener(() => {
      setWakeLockActive(false);
    });

    // Safely check and subscribe to battery changes (Chrome / Edge / Opera on Mac & Windows)
    batteryGuard.init().then((state) => setBatteryState(state));
    const unsubscribeBattery = batteryGuard.subscribe((state) => {
      setBatteryState(state);
    });

    // Handle visibilitychange to re-acquire wake lock if tab re-focused
    const handleVisibility = async () => {
      if (document.visibilityState === 'visible' && isRunning) {
        const acquired = await wakeLockService.request();
        setWakeLockActive(acquired);
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      unsubscribeBattery();
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [isRunning]);

  // Battery Guard auto-stop: protects laptop hardware if battery drops below 15% while discharging
  useEffect(() => {
    if (
      isRunning &&
      batteryState.supported &&
      batteryState.charging === false &&
      batteryState.level !== null &&
      batteryState.level <= 15
    ) {
      handleStop();
      setBatteryStopNotice(
        `Battery Guard: Stopped automatically at ${batteryState.level}% battery to protect hardware.`
      );
    }
  }, [isRunning, batteryState]);

  // Handle pulse animation while running
  useEffect(() => {
    if (!isRunning) {
      setPulseState(false);
      return;
    }

    const pulseInterval = window.setInterval(() => {
      setPulseState((prev) => !prev);
    }, 800);
    pulseTimerRef.current = pulseInterval;

    return () => {
      window.clearInterval(pulseInterval);
    };
  }, [isRunning]);

  // Execute keep-alive signal tick
  const triggerNudge = useCallback(() => {
    setSignalsCount((prev) => prev + 1);
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    setLastSignalTime(timeStr);

    if (soundEnabled) {
      playSignalChime();
    }
  }, [soundEnabled]);

  // Background Web Worker keep-alive interval loop (unthrottled on background tabs)
  useEffect(() => {
    if (!isRunning) {
      if (heartbeatWorkerRef.current) {
        heartbeatWorkerRef.current.stop();
        heartbeatWorkerRef.current.destroy();
        heartbeatWorkerRef.current = null;
      }
      return;
    }

    const parsedSec = Math.max(1, parseInt(intervalSec, 10) || 30);
    // Initial immediate nudge on start
    triggerNudge();

    const worker = new BackgroundHeartbeat();
    heartbeatWorkerRef.current = worker;
    worker.start(parsedSec * 1000, () => {
      triggerNudge();
    });

    return () => {
      worker.stop();
      worker.destroy();
    };
  }, [isRunning, intervalSec, triggerNudge]);

  // Power action timer countdown
  useEffect(() => {
    if (!isRunning || !powerDeadline) {
      if (powerCountdownRef.current) {
        window.clearInterval(powerCountdownRef.current);
        powerCountdownRef.current = null;
      }
      return;
    }

    const checkDeadline = () => {
      if (Date.now() >= powerDeadline) {
        setPowerDeadline(null);
        setShowPowerWarning(true);
      }
    };

    const countdown = window.setInterval(checkDeadline, 1000);
    powerCountdownRef.current = countdown;

    return () => {
      window.clearInterval(countdown);
    };
  }, [isRunning, powerDeadline]);

  // Apply Quick Preset
  const handleSelectPreset = (preset: PresetConfig) => {
    if (isRunning) return;
    setSelectedPresetId(preset.id);
    setIntervalSec(preset.interval);
    setPowerAction(preset.action);
    setPowerTime(preset.time);
  };

  // START action
  const handleStart = async () => {
    setExecutedPowerAction(null);
    setBatteryStopNotice(null);
    let sec = parseInt(intervalSec, 10);
    if (isNaN(sec) || sec < 1) {
      sec = 30;
      setIntervalSec('30');
    }

    setIsRunning(true);

    // Request screen wake lock
    if (wakeLockService.isSupported()) {
      const success = await wakeLockService.request();
      setWakeLockActive(success);
    }

    // Arm power action if selected
    if (powerAction !== 'Off' && powerTime.trim()) {
      const deadline = parsePowerDeadline(powerTime);
      setPowerDeadline(deadline);
    } else {
      setPowerDeadline(null);
    }
  };

  // STOP action
  const handleStop = async () => {
    setIsRunning(false);
    setPowerDeadline(null);
    setShowPowerWarning(false);
    await wakeLockService.release();
    setWakeLockActive(false);
  };

  // Execute power action
  const handleExecutePowerAction = (action: string) => {
    setShowPowerWarning(false);
    handleStop();
    setExecutedPowerAction(action);
  };

  return (
    <main className="min-h-screen bg-[#11111b] text-[#cdd6f4] flex flex-col items-center justify-center p-4 selection:bg-[#94e2d5] selection:text-[#11111b]">
      {/* Desktop App Window Container */}
      <div
        id="app-window"
        className="w-full max-w-[480px] rounded-2xl bg-[#11111b] border border-[#313244] shadow-2xl p-6 sm:p-7 flex flex-col relative"
      >
        {/* Window Top Controls & Tools */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#f38ba8]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#fab387]/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-[#a6e3a1]/80 inline-block" />
          </div>

          <div className="flex items-center gap-1.5">
            {/* Battery Guard Badge (if supported) */}
            {batteryState.supported && batteryState.level !== null && (
              <div
                title={
                  batteryState.charging
                    ? `Battery: ${batteryState.level}% (Charging)`
                    : `Battery: ${batteryState.level}% (Guard active under 15%)`
                }
                className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${
                  batteryState.level <= 15
                    ? 'border-[#f38ba8]/60 bg-[#f38ba8]/10 text-[#f38ba8]'
                    : 'border-[#313244] bg-[#181825] text-[#a6adc8]'
                }`}
              >
                {batteryState.charging ? (
                  <BatteryCharging className="w-3 h-3 text-[#a6e3a1]" />
                ) : batteryState.level <= 20 ? (
                  <BatteryWarning className="w-3 h-3 text-[#f38ba8]" />
                ) : (
                  <Battery className="w-3 h-3 text-[#94e2d5]" />
                )}
                <span>{batteryState.level}%</span>
              </div>
            )}

            {/* Launch Kit Button */}
            <button
              id="open-launch-kit-btn"
              type="button"
              onClick={() => setShowLaunchKitModal(true)}
              title="Product Hunt Launch Kit (Assets & Copy)"
              className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium text-[#fab387] bg-[#fab387]/10 border border-[#fab387]/30 hover:bg-[#fab387]/20 transition-colors cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Launch Kit</span>
            </button>

            {/* Audio chime toggle */}
            <button
              id="toggle-sound-btn"
              type="button"
              onClick={() => setSoundEnabled((v) => !v)}
              title={soundEnabled ? 'Mute signal chimes' : 'Enable audio chimes on signal'}
              className="p-1.5 rounded-md text-[#a6adc8] hover:text-[#cdd6f4] hover:bg-[#181825] transition-colors cursor-pointer"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4 text-[#a6e3a1]" /> : <VolumeX className="w-4 h-4 text-[#585b70]" />}
            </button>

            {/* CLI Modal button */}
            <button
              id="open-cli-modal-btn"
              type="button"
              onClick={() => setShowDesktopModal(true)}
              title="View Python CLI / Desktop details"
              className="flex items-center gap-1 px-2 py-1 rounded-md text-xs text-[#a6adc8] bg-[#181825] border border-[#313244] hover:text-[#94e2d5] transition-colors cursor-pointer"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>CLI</span>
            </button>
          </div>
        </div>

        {/* Title Header */}
        <header className="text-center mb-4">
          <h1
            id="app-heading"
            className="text-2xl font-bold tracking-tight text-[#cdd6f4] flex items-center justify-center gap-2"
          >
            <span>⚡</span> Keep Awake
          </h1>
          <p className="text-xs text-[#585b70] mt-1 font-normal">
            Keeps AI agents running — no lock, sleep or display-off
          </p>
        </header>

        {/* Status Card */}
        <section
          id="status-card"
          className={`rounded-xl bg-[#181825] border transition-all duration-300 py-4 px-5 text-center mb-4 ${
            isRunning
              ? 'border-[#a6e3a1] shadow-lg shadow-[#a6e3a1]/10'
              : 'border-[#585b70]/60'
          }`}
        >
          <div className="flex items-center justify-center gap-2.5 mb-2">
            <span
              id="pulse-indicator"
              className={`w-3.5 h-3.5 rounded-full transition-colors duration-300 ${
                isRunning
                  ? pulseState
                    ? 'bg-[#a6e3a1] shadow-[0_0_8px_#a6e3a1]'
                    : 'bg-[#40a040]'
                  : 'bg-[#f38ba8]'
              }`}
            />
            <span
              id="status-label"
              className={`font-semibold tracking-wider text-sm uppercase ${
                isRunning ? 'text-[#a6e3a1]' : 'text-[#f38ba8]'
              }`}
            >
              {isRunning ? 'ACTIVE' : 'INACTIVE'}
            </span>
          </div>

          <div className="flex items-center justify-center gap-3 text-xs text-[#a6adc8] mt-2">
            <span id="moves-label" className="font-mono">
              Signals: {signalsCount}
            </span>
            <span className="text-[#585b70]">•</span>
            <span id="time-label" className="font-mono">
              Last: {lastSignalTime || '--:--:--'}
            </span>
          </div>

          {/* Wake Lock & Background Worker Badge */}
          {isRunning && (
            <div className="mt-3 pt-2.5 border-t border-[#313244]/60 flex items-center justify-center gap-2 text-[11px] text-[#94e2d5]">
              <MonitorUp className="w-3.5 h-3.5" />
              <span>
                {wakeLockActive
                  ? 'Screen Wake Lock Engaged'
                  : 'Periodic Keep-Alive Active'}
              </span>
              <span className="text-[#585b70]">•</span>
              <span className="text-[#a6adc8]">Background Worker Active</span>
            </div>
          )}
        </section>

        {/* Battery Guard Auto-stop Notice */}
        {batteryStopNotice && (
          <div
            id="battery-stop-notice"
            className="mb-4 p-3 rounded-lg bg-[#181825] border border-[#f38ba8]/50 text-center text-xs text-[#f38ba8] flex items-center justify-center gap-2"
          >
            <ShieldCheck className="w-4 h-4 text-[#f38ba8]" />
            <span>{batteryStopNotice}</span>
          </div>
        )}

        {/* Executed Power Action Notice */}
        {executedPowerAction && (
          <div
            id="power-action-notice"
            className="mb-4 p-3 rounded-lg bg-[#181825] border border-[#fab387]/50 text-center text-xs text-[#fab387]"
          >
            <div className="flex items-center justify-center gap-1.5 font-medium mb-1">
              <Power className="w-4 h-4" />
              <span>Simulated {executedPowerAction} Executed</span>
            </div>
            <p className="text-[#a6adc8] text-[11px]">
              Keep-awake session released. You can restart anytime.
            </p>
          </div>
        )}

        {/* Quick Presets Selector */}
        <div id="quick-presets-group" className="mb-4">
          <div className="text-[11px] font-semibold text-[#a6adc8] mb-1.5 text-center">
            Quick Presets:
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
            {PRESETS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                disabled={isRunning}
                onClick={() => handleSelectPreset(preset)}
                className={`px-2 py-1.5 rounded-lg text-[11px] font-medium border transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${
                  selectedPresetId === preset.id
                    ? 'border-[#a6e3a1] bg-[#a6e3a1]/10 text-[#a6e3a1]'
                    : 'border-[#313244] bg-[#181825] text-[#a6adc8] hover:border-[#585b70]'
                }`}
              >
                <span>{preset.emoji}</span> {preset.name}
              </button>
            ))}
          </div>
        </div>

        {/* Interval Control */}
        <div id="interval-control-group" className="flex items-center justify-center gap-2 mb-4">
          <label htmlFor="interval-input" className="text-xs text-[#a6adc8]">
            Interval
          </label>
          <input
            id="interval-input"
            type="number"
            min="1"
            max="3600"
            disabled={isRunning}
            value={intervalSec}
            onChange={(e) => {
              setIntervalSec(e.target.value);
              setSelectedPresetId('');
            }}
            className="w-16 rounded-md border border-[#585b70] bg-[#181825] px-2 py-1 text-center font-mono text-sm font-semibold text-[#cdd6f4] focus:border-[#94e2d5] focus:outline-hidden disabled:opacity-60"
          />
          <span className="text-xs text-[#585b70]">sec</span>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <button
            id="start-btn"
            type="button"
            disabled={isRunning}
            onClick={handleStart}
            className={`flex items-center justify-center gap-1.5 rounded-lg py-2.5 px-4 font-semibold text-xs tracking-wide transition-all duration-200 cursor-pointer ${
              isRunning
                ? 'bg-[#181825] text-[#585b70] cursor-not-allowed opacity-60'
                : 'bg-[#a6e3a1] text-[#11111b] hover:bg-[#94e2d5] active:scale-98 shadow-md'
            }`}
          >
            <span>▶</span>
            <span>START</span>
          </button>

          <button
            id="stop-btn"
            type="button"
            disabled={!isRunning}
            onClick={handleStop}
            className={`flex items-center justify-center gap-1.5 rounded-lg py-2.5 px-4 font-semibold text-xs tracking-wide transition-all duration-200 cursor-pointer ${
              !isRunning
                ? 'bg-[#181825] text-[#585b70] cursor-not-allowed opacity-60'
                : 'bg-[#f38ba8] text-[#11111b] hover:brightness-105 active:scale-98 shadow-md'
            }`}
          >
            <span>⏹</span>
            <span>STOP</span>
          </button>
        </div>

        {/* Options */}
        <section id="options-section" className="space-y-3 pt-2 border-t border-[#313244]/60">
          {/* Scheduled power action */}
          <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
            <span className="text-[#a6adc8]">Then</span>
            <select
              id="power-action-select"
              disabled={isRunning}
              value={powerAction}
              onChange={(e) => {
                setPowerAction(e.target.value);
                setSelectedPresetId('');
              }}
              className="rounded-md border border-[#313244] bg-[#181825] px-2 py-1 text-xs text-[#cdd6f4] focus:border-[#94e2d5] focus:outline-hidden disabled:opacity-60 cursor-pointer"
            >
              <option value="Off">Off</option>
              <option value="Sleep">Sleep</option>
              <option value="Hibernate">Hibernate</option>
              <option value="Shutdown">Shutdown</option>
            </select>

            <span className="text-[#a6adc8]">after</span>
            <input
              id="power-time-input"
              type="text"
              placeholder="e.g. 60"
              disabled={isRunning}
              value={powerTime}
              onChange={(e) => {
                setPowerTime(e.target.value);
                setSelectedPresetId('');
              }}
              className="w-20 rounded-md border border-[#313244] bg-[#181825] px-2 py-1 text-center font-mono text-xs text-[#cdd6f4] focus:border-[#94e2d5] focus:outline-hidden disabled:opacity-60"
            />
            <span className="text-[11px] text-[#585b70]">min / HH:MM</span>
          </div>

          {/* Lid-close checkbox */}
          <div className="flex items-center justify-center gap-2 text-xs">
            <label className="flex items-center gap-2 cursor-pointer select-none text-[#a6adc8] hover:text-[#cdd6f4]">
              <input
                id="lid-close-checkbox"
                type="checkbox"
                checked={lidClosedStayAwake}
                onChange={(e) => setLidClosedStayAwake(e.target.checked)}
                className="rounded border-[#585b70] bg-[#181825] text-[#a6e3a1] focus:ring-0 focus:ring-offset-0 cursor-pointer"
              />
              <span>Stay awake even with the lid closed</span>
            </label>
          </div>

          {/* Run at login checkbox */}
          <div className="flex items-center justify-center gap-2 text-xs">
            <label className="flex items-center gap-2 cursor-pointer select-none text-[#a6adc8] hover:text-[#cdd6f4]">
              <input
                id="autostart-checkbox"
                type="checkbox"
                checked={startAtLogin}
                onChange={(e) => setStartAtLogin(e.target.checked)}
                className="rounded border-[#585b70] bg-[#181825] text-[#a6e3a1] focus:ring-0 focus:ring-offset-0 cursor-pointer"
              />
              <span>Start automatically at login</span>
            </label>
          </div>
        </section>

        {/* Footer Notes */}
        <footer className="mt-5 pt-4 border-t border-[#313244]/60 text-center space-y-2">
          <p className="text-[11px] text-[#585b70]">
            ✕ exits &nbsp;•&nbsp; — minimize hides to the tray
          </p>
          <p className="text-[10px] text-[#585b70] max-w-xs mx-auto leading-relaxed">
            Lid-closed stay-awake changes the power plan while running and restores it on STOP/exit.
          </p>

          {/* Credit */}
          <div className="pt-2 text-[11px] text-[#585b70] flex items-center justify-center gap-1">
            <span>Developed with</span>
            <span className="text-[#f38ba8]">♥</span>
            <span>by</span>
            <a
              id="author-credit-link"
              href="https://bit.ly/atozaboutdata"
              target="_blank"
              rel="noreferrer"
              className="text-[#94e2d5] font-semibold underline hover:text-[#a6e3a1] transition-colors"
            >
              MAHANTESH HIREMATH
            </a>
          </div>
        </footer>
      </div>

      {/* 30-second cancelable warning dialog */}
      {showPowerWarning && (
        <PowerWarningModal
          action={powerAction}
          onCancel={() => setShowPowerWarning(false)}
          onExecute={handleExecutePowerAction}
        />
      )}

      {/* CLI / Desktop Information Modal */}
      {showDesktopModal && (
        <DesktopScriptModal onClose={() => setShowDesktopModal(false)} />
      )}

      {/* Product Hunt Launch Kit Modal */}
      {showLaunchKitModal && (
        <LaunchKitModal onClose={() => setShowLaunchKitModal(false)} />
      )}
    </main>
  );
}

