import { useState } from 'react';
import { Copy, Check, Download, ExternalLink, X, Sparkles, Image, FileText, Video } from 'lucide-react';

interface LaunchKitModalProps {
  onClose: () => void;
}

export function LaunchKitModal({ onClose }: LaunchKitModalProps) {
  const [activeTab, setActiveTab] = useState<'copy' | 'assets' | 'pitch'>('copy');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const copyData = {
    name: "Don't Lock My PC",
    tagline: "Keep your PC awake while AI agents do the heavy lifting",
    topics: "Developer Tools, Artificial Intelligence, Open Source, Productivity, Mac & Windows",
    description:
      "Long-running AI agents, model downloads, and automated workflows shouldn't be interrupted by corporate lock screens or sleep timers. Don't Lock My PC keeps your system awake without registry hacks, then auto-powers down when your work is finished.",
    firstComment: `Hey Product Hunt! 👋

I'm Mahantesh, creator of Don't Lock My PC.

Like many of you, I've been running more autonomous AI agents (Claude Computer Use, AutoGen, long batch evaluations) and large dataset transfers that run for hours.

The problem: You step away for lunch or head to sleep, and strict corporate or OS power policies kick in—locking the session, cutting RDP connections, or putting the machine to sleep mid-run.

⚡ Why Don't Lock My PC is different:
1. One-Click Keep Awake: Simple, non-intrusive signals keep your screen and session awake without interfering with your windows.
2. Scheduled Auto-Power: Set your agent to run for 2 hours, and configure Don't Lock My PC to automatically sleep, hibernate, or shutdown afterwards—complete with a 30-second cancelable warning dialog.
3. Smart Battery Guard: Automatically releases keep-awake if battery dips below 15% to protect laptop hardware.
4. Lid-Closed Stay Awake: Keep running tasks even when your laptop is closed or in dock mode, safely restoring power plans on exit.
5. Flexible Formats: Use it as a native desktop app, a headless Python CLI (pip install dontlockpc), or directly in your browser with zero installs.

It is 100% free and open source on GitHub:
👉 https://github.com/mahanteshimath/do-not-lock-my-system

I’d love to hear your feedback, feature requests, and what AI workflows you're keeping awake!`,
  };

  return (
    <div
      id="launch-kit-backdrop"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-3 sm:p-4 animate-in fade-in duration-150"
    >
      <div
        id="launch-kit-modal"
        className="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl border border-[#313244] bg-[#181825] shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#313244] bg-[#11111b]/60">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-[#fab387]/15 text-[#fab387]">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-[#cdd6f4]">Product Hunt Launch Kit</h3>
              <p className="text-[11px] text-[#a6adc8]">Everything ready for your launch submission</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#a6adc8] hover:text-[#cdd6f4] hover:bg-[#313244] cursor-pointer transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-[#313244] bg-[#11111b]/30 px-5 pt-2 gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('copy')}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
              activeTab === 'copy'
                ? 'border-[#a6e3a1] text-[#a6e3a1]'
                : 'border-transparent text-[#a6adc8] hover:text-[#cdd6f4]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Copy & Pitch</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('assets')}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
              activeTab === 'assets'
                ? 'border-[#94e2d5] text-[#94e2d5]'
                : 'border-transparent text-[#a6adc8] hover:text-[#cdd6f4]'
            }`}
          >
            <Image className="w-3.5 h-3.5" />
            <span>Graphics & Gallery (4)</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('pitch')}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 cursor-pointer transition-colors ${
              activeTab === 'pitch'
                ? 'border-[#fab387] text-[#fab387]'
                : 'border-transparent text-[#a6adc8] hover:text-[#cdd6f4]'
            }`}
          >
            <Video className="w-3.5 h-3.5" />
            <span>Demo & Loom Guide</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="overflow-y-auto p-5 space-y-4 text-xs">
          {activeTab === 'copy' && (
            <div className="space-y-4">
              {/* Name & Tagline */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-[#cdd6f4]">Tagline (under 60 chars):</span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(copyData.tagline, 'tagline')}
                    className="flex items-center gap-1 text-[11px] text-[#a6e3a1] hover:underline cursor-pointer"
                  >
                    {copiedKey === 'tagline' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'tagline' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <div className="font-mono text-[11px] text-[#a6e3a1]">{copyData.tagline}</div>
                <div className="text-[10px] text-[#585b70] mt-1">Length: 58 characters</div>
              </div>

              {/* Topics */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-[#cdd6f4]">Topics / Categories:</span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(copyData.topics, 'topics')}
                    className="flex items-center gap-1 text-[11px] text-[#a6e3a1] hover:underline cursor-pointer"
                  >
                    {copiedKey === 'topics' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'topics' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <div className="text-[11px] text-[#cdd6f4]">{copyData.topics}</div>
              </div>

              {/* Short Pitch / Description */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-[#cdd6f4]">Description / Pitch (260 char limit):</span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(copyData.description, 'description')}
                    className="flex items-center gap-1 text-[11px] text-[#a6e3a1] hover:underline cursor-pointer"
                  >
                    {copiedKey === 'description' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'description' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <p className="text-[11px] text-[#a6adc8] leading-relaxed">{copyData.description}</p>
                <div className="text-[10px] text-[#585b70] mt-1">Length: 247 characters</div>
              </div>

              {/* First Maker Comment */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-[#cdd6f4]">First Maker Comment (Launch day):</span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(copyData.firstComment, 'comment')}
                    className="flex items-center gap-1 text-[11px] text-[#a6e3a1] hover:underline cursor-pointer"
                  >
                    {copiedKey === 'comment' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'comment' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <pre className="text-[10px] text-[#a6adc8] font-mono whitespace-pre-wrap max-h-40 overflow-y-auto p-2 bg-[#181825] rounded border border-[#313244]">
                  {copyData.firstComment}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'assets' && (
            <div className="space-y-4">
              <p className="text-xs text-[#a6adc8]">
                All assets are crafted to exact Product Hunt requirements and hosted directly in your app bundle:
              </p>

              {/* 1. Thumbnail */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244] flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <img
                    src="/product-hunt-thumbnail.svg"
                    alt="240x240 Thumbnail"
                    className="w-14 h-14 rounded-xl border border-[#313244] bg-[#181825] p-1"
                  />
                  <div>
                    <div className="font-semibold text-[#cdd6f4]">Thumbnail Icon</div>
                    <div className="text-[10px] text-[#585b70]">240 × 240px (Max 2MB) • Square SVG</div>
                  </div>
                </div>
                <a
                  href="/product-hunt-thumbnail.svg"
                  download="ph-thumbnail-240x240.svg"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#a6e3a1] text-[#11111b] font-semibold text-xs hover:bg-[#94e2d5] transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>

              {/* 2. Gallery 1 */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244] flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <img
                    src="/product-hunt-gallery-1.svg"
                    alt="Gallery 1"
                    className="w-20 h-12 object-cover rounded-lg border border-[#313244]"
                  />
                  <div>
                    <div className="font-semibold text-[#cdd6f4]">Gallery 1 (Hero Preview)</div>
                    <div className="text-[10px] text-[#585b70]">1270 × 760px • Active UI & Zero-Registry Value</div>
                  </div>
                </div>
                <a
                  href="/product-hunt-gallery-1.svg"
                  download="ph-gallery-1-hero.svg"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#313244] text-[#cdd6f4] font-semibold text-xs hover:bg-[#45475a] transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>

              {/* 3. Gallery 2 */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244] flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <img
                    src="/product-hunt-gallery-2.svg"
                    alt="Gallery 2"
                    className="w-20 h-12 object-cover rounded-lg border border-[#313244]"
                  />
                  <div>
                    <div className="font-semibold text-[#cdd6f4]">Gallery 2 (Power & Safety)</div>
                    <div className="text-[10px] text-[#585b70]">1270 × 760px • Timed Shutdown, 30s Safety Beep, Lid Closed</div>
                  </div>
                </div>
                <a
                  href="/product-hunt-gallery-2.svg"
                  download="ph-gallery-2-power.svg"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#313244] text-[#cdd6f4] font-semibold text-xs hover:bg-[#45475a] transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>

              {/* 4. Gallery 3 */}
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244] flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <img
                    src="/product-hunt-gallery-3.svg"
                    alt="Gallery 3"
                    className="w-20 h-12 object-cover rounded-lg border border-[#313244]"
                  />
                  <div>
                    <div className="font-semibold text-[#cdd6f4]">Gallery 3 (AI Agents & CLI)</div>
                    <div className="text-[10px] text-[#585b70]">1270 × 760px • Python Backend, Claude Computer Use, CI</div>
                  </div>
                </div>
                <a
                  href="/product-hunt-gallery-3.svg"
                  download="ph-gallery-3-agents.svg"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#313244] text-[#cdd6f4] font-semibold text-xs hover:bg-[#45475a] transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>
            </div>
          )}

          {activeTab === 'pitch' && (
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244]">
                <div className="font-semibold text-[#cdd6f4] mb-1">Interactive Demo URL for Product Hunt:</div>
                <p className="text-[11px] text-[#a6adc8] mb-2">
                  You can paste this live URL directly into the Product Hunt &ldquo;Link to the demo&rdquo; field or create an Arcade / Supademo flow:
                </p>
                <div className="flex items-center justify-between p-2 rounded bg-[#181825] border border-[#313244] text-[#94e2d5] font-mono text-[10px]">
                  <span>https://ais-pre-me5cpvjwto3kdrwvx7xwq5-118203415033.asia-southeast1.run.app/</span>
                  <button
                    type="button"
                    onClick={() =>
                      copyToClipboard(
                        'https://ais-pre-me5cpvjwto3kdrwvx7xwq5-118203415033.asia-southeast1.run.app/',
                        'demoUrl'
                      )
                    }
                    className="text-[#cdd6f4] hover:text-[#a6e3a1] cursor-pointer"
                  >
                    {copiedKey === 'demoUrl' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[#11111b] border border-[#313244] space-y-2">
                <div className="font-semibold text-[#cdd6f4]">60-Second Loom / Video Script Outline:</div>
                <div className="space-y-1.5 text-[11px] text-[#a6adc8]">
                  <div>
                    <strong className="text-[#fab387]">0:00 - 0:12:</strong> The Pain Point: Leaving long AI agent jobs or model downloads running only to find Windows/macOS locked after 5 mins.
                  </div>
                  <div>
                    <strong className="text-[#94e2d5]">0:12 - 0:28:</strong> The Solution: Click START on Don&rsquo;t Lock My PC. Instant Screen Wake Lock and periodic unthrottled keep-alive pulses.
                  </div>
                  <div>
                    <strong className="text-[#a6e3a1]">0:28 - 0:45:</strong> Power Timers & Safety: Set 2-hour shutdown with 30s audio warning. Battery Guard auto-shuts off if below 15%.
                  </div>
                  <div>
                    <strong className="text-[#cdd6f4]">0:45 - 1:00:</strong> Call to Action: Zero install web tab or <code className="text-[#a6e3a1]">pip install dontlockpc</code>. 100% Free & Open Source.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#313244] bg-[#11111b]/60">
          <a
            href="https://github.com/mahanteshimath/do-not-lock-my-system"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-xs text-[#94e2d5] hover:underline"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-3 h-3" />
          </a>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#313244] text-xs font-semibold text-[#cdd6f4] hover:bg-[#45475a] cursor-pointer transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
