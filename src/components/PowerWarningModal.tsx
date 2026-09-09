import { useEffect, useState } from 'react';
import { playWarningBeep } from '../utils/wakeLock';

interface PowerWarningModalProps {
  action: string;
  onCancel: () => void;
  onExecute: (action: string) => void;
}

export function PowerWarningModal({ action, onCancel, onExecute }: PowerWarningModalProps) {
  const [countdown, setCountdown] = useState(30);

  useEffect(() => {
    playWarningBeep();
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onExecute(action);
          return 0;
        }
        if (prev % 5 === 0 || prev <= 5) {
          playWarningBeep();
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [action, onExecute]);

  return (
    <div
      id="power-warning-backdrop"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4"
    >
      <div
        id="power-warning-modal"
        className="w-full max-w-sm rounded-xl border border-[#f38ba8]/40 bg-[#181825] p-6 shadow-2xl text-center animate-in fade-in zoom-in-95 duration-200"
      >
        <div className="flex items-center justify-center gap-2 mb-3 text-[#f38ba8]">
          <span className="inline-block w-3 h-3 rounded-full bg-[#f38ba8] animate-ping" />
          <h3 className="font-semibold text-lg text-[#cdd6f4]">Power Action Warning</h3>
        </div>

        <p className="text-sm text-[#cdd6f4] my-4 leading-relaxed">
          System will <span className="font-semibold text-[#fab387]">{action.toLowerCase()}</span> in{' '}
          <span className="font-mono text-xl font-bold text-[#f38ba8] px-2 py-0.5 rounded bg-[#11111b]">
            {countdown}s
          </span>
        </p>

        <p className="text-xs text-[#a6adc8] mb-6">
          Keep-awake signals will be halted automatically before powering down.
        </p>

        <div className="flex gap-3 justify-center">
          <button
            id="cancel-power-action-btn"
            type="button"
            onClick={onCancel}
            className="w-full max-w-[200px] cursor-pointer rounded-lg bg-[#a6e3a1] px-6 py-2.5 text-sm font-semibold text-[#11111b] transition-colors hover:bg-[#94e2d5] active:scale-98"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
