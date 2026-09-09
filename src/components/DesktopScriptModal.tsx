import { useState } from 'react';
import { Copy, Check, Terminal, ExternalLink, X } from 'lucide-react';

interface DesktopScriptModalProps {
  onClose: () => void;
}

export function DesktopScriptModal({ onClose }: DesktopScriptModalProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const copyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(id);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const pipCommand = `pip install dontlockpc\ndontlockpc`;
  const headlessScript = `from dontlockpc.backends import get_backend
import time

backend = get_backend()
backend.prevent_sleep()
try:
    while True:
        backend.nudge()  # sends invisible F15 + ±1px mouse nudge
        time.sleep(30)
finally:
    backend.allow_sleep()
    backend.close()`;

  return (
    <div
      id="desktop-script-backdrop"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4"
    >
      <div
        id="desktop-script-modal"
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-xl border border-[#585b70] bg-[#181825] p-6 shadow-2xl text-left"
      >
        <div className="flex items-center justify-between pb-3 border-b border-[#313244]">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-[#94e2d5]" />
            <h3 className="font-semibold text-base text-[#cdd6f4]">
              Native Desktop & Headless CLI
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-[#a6adc8] hover:text-[#cdd6f4] hover:bg-[#313244] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="mt-4 space-y-4 text-xs text-[#a6adc8]">
          <p>
            This web app provides browser-level keep-awake using the{' '}
            <strong className="text-[#cdd6f4]">Screen Wake Lock API</strong>. If you need native OS-level
            sleep prevention or lid-close overrides for Windows or macOS terminals:
          </p>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-[#cdd6f4]">Run via Python CLI:</span>
              <button
                type="button"
                onClick={() => copyText(pipCommand, 'pip')}
                className="flex items-center gap-1 text-[11px] text-[#94e2d5] hover:underline cursor-pointer"
              >
                {copiedSection === 'pip' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#a6e3a1]" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" /> Copy
                  </>
                )}
              </button>
            </div>
            <pre className="p-2.5 rounded bg-[#11111b] border border-[#313244] text-[#a6e3a1] font-mono text-[11px] overflow-x-auto">
              {pipCommand}
            </pre>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-[#cdd6f4]">Headless Script (CI / Long Agent Jobs):</span>
              <button
                type="button"
                onClick={() => copyText(headlessScript, 'script')}
                className="flex items-center gap-1 text-[11px] text-[#94e2d5] hover:underline cursor-pointer"
              >
                {copiedSection === 'script' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#a6e3a1]" /> Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" /> Copy
                  </>
                )}
              </button>
            </div>
            <pre className="p-2.5 rounded bg-[#11111b] border border-[#313244] text-[#cdd6f4] font-mono text-[10px] overflow-x-auto">
              {headlessScript}
            </pre>
          </div>

          <div className="pt-2 border-t border-[#313244] space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[#cdd6f4]">Product Hunt Launch Assets:</span>
              <span className="text-[10px] text-[#a6e3a1]">Ready to upload</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <a
                href="/product-hunt-thumbnail.svg"
                target="_blank"
                download="ph-thumbnail-240x240.svg"
                className="flex items-center justify-center gap-1 p-1.5 rounded bg-[#11111b] border border-[#313244] text-[#94e2d5] hover:border-[#94e2d5]"
              >
                <span>Thumbnail (240x240)</span>
              </a>
              <a
                href="/product-hunt-gallery-1.svg"
                target="_blank"
                download="ph-gallery-1.svg"
                className="flex items-center justify-center gap-1 p-1.5 rounded bg-[#11111b] border border-[#313244] text-[#94e2d5] hover:border-[#94e2d5]"
              >
                <span>Gallery 1 (Hero)</span>
              </a>
              <a
                href="/product-hunt-gallery-2.svg"
                target="_blank"
                download="ph-gallery-2.svg"
                className="flex items-center justify-center gap-1 p-1.5 rounded bg-[#11111b] border border-[#313244] text-[#94e2d5] hover:border-[#94e2d5]"
              >
                <span>Gallery 2 (Power)</span>
              </a>
              <a
                href="/product-hunt-gallery-3.svg"
                target="_blank"
                download="ph-gallery-3.svg"
                className="flex items-center justify-center gap-1 p-1.5 rounded bg-[#11111b] border border-[#313244] text-[#94e2d5] hover:border-[#94e2d5]"
              >
                <span>Gallery 3 (Agents)</span>
              </a>
            </div>
          </div>

          <div className="pt-2 border-t border-[#313244] flex items-center justify-between">
            <span>Source repository:</span>
            <a
              href="https://github.com/mahanteshimath/do-not-lock-my-system"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-[#94e2d5] hover:underline"
            >
              mahanteshimath/do-not-lock-my-system
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg bg-[#313244] px-4 py-1.5 text-xs font-semibold text-[#cdd6f4] hover:bg-[#45475a] cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
