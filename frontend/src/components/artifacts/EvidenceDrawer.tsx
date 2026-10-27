import React, { useEffect } from 'react';
import { X, ExternalLink, FileCode, CheckCircle2 } from 'lucide-react';
import type { Finding } from '../../types/contract';
import { ProvenanceStamp } from '../ui/ProvenanceStamp';

interface EvidenceDrawerProps {
  finding: Finding | null;
  isOpen: boolean;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  finding,
  isOpen,
  onClose,
}) => {
  // Listen for Esc key to close drawer (Accessibility affordance)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !finding) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-[2px] transition-opacity"
      role="dialog"
      aria-modal="true"
      aria-labelledby="drawer-title"
    >
      {/* Click outside to dismiss */}
      <div className="flex-1" onClick={onClose} aria-hidden="true" />

      {/* Drawer Surface */}
      <div className="w-full max-w-lg bg-bg-1 border-l border-line h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-line bg-bg-0">
          <div className="flex items-center gap-2.5">
            <span className="font-mono text-xs text-text-2 bg-bg-2 border border-line px-1.5 py-0.5 rounded-[2px]">
              {finding.id}
            </span>
            <h3 id="drawer-title" className="font-mono text-sm font-semibold text-text-0">
              {finding.label}
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <ProvenanceStamp confidence={finding.confidence} />
            <button
              onClick={onClose}
              aria-label="Close evidence drawer"
              className="text-text-2 hover:text-text-0 p-1 border border-line hover:border-line-strong rounded-[2px] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 flex-1 overflow-y-auto space-y-4">
          <div className="bg-bg-0 p-3 border border-line rounded-[2px]">
            <span className="font-mono text-[11px] text-text-2 uppercase tracking-wider block mb-1">
              Finding Summary
            </span>
            <p className="text-sm text-text-1">{finding.summary}</p>
          </div>

          <div>
            <h4 className="font-mono text-xs uppercase tracking-wider text-text-2 mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan" />
              <span>Verifiable Evidence Records ({finding.evidence.length})</span>
            </h4>

            <div className="space-y-2.5">
              {finding.evidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="bg-bg-0 border border-line p-3 rounded-[2px] space-y-2 hover:border-line-strong transition-colors"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 font-mono text-xs text-text-0 font-medium truncate">
                      <FileCode className="w-3.5 h-3.5 text-text-2 shrink-0" />
                      <span className="truncate">{ev.path}</span>
                    </div>
                    {ev.github_url && (
                      <a
                        href={ev.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] font-mono text-cyan hover:underline shrink-0 bg-cyan/5 px-2 py-0.5 border border-cyan/20 rounded-[2px]"
                      >
                        <span>View on GitHub</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                  <p className="text-xs text-text-1 font-mono leading-relaxed bg-bg-2 p-2 border border-line rounded-[2px]">
                    {ev.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-line bg-bg-0 font-mono text-[11px] text-text-2 flex items-center justify-between">
          <span>Press ESC or click outside to dismiss</span>
          <span>Archaeological Survey</span>
        </div>
      </div>
    </div>
  );
};
