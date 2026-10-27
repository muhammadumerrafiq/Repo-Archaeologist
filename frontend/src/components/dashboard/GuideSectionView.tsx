import React from 'react';
import { BookOpen } from 'lucide-react';
import type { GuideSection } from '../../types/contract';

interface GuideSectionViewProps {
  guide: GuideSection[];
}

export const GuideSectionView: React.FC<GuideSectionViewProps> = ({ guide }) => {
  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan" />
          <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider">
            Deterministic Architectural Guide
          </h2>
        </div>
        <span className="font-mono text-xs text-text-2">
          Evidence-backed synthesis
        </span>
      </div>

      <p className="text-xs text-text-1 leading-relaxed">
        This structural narrative is synthesized strictly by deterministic rules from observed codebase facts, entry
        candidates, and declared manifests. Zero generative AI hallucinations.
      </p>

      {guide.length === 0 ? (
        <div className="p-6 text-center text-text-2 font-mono text-xs border border-dashed border-border rounded">
          Insufficient findings to synthesize a narrative guide.
        </div>
      ) : (
        <div className="space-y-4">
          {guide.map((section) => (
            <div
              key={section.title}
              className="p-4 rounded bg-bg-2 border border-border space-y-2"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-mono text-xs font-bold text-cyan uppercase tracking-wider">
                  {section.title}
                </h3>
                {section.finding_refs.length > 0 && (
                  <div className="flex items-center gap-1">
                    {section.finding_refs.map((ref) => (
                      <span
                        key={ref}
                        className="text-[10px] font-mono text-text-2 bg-bg-0 px-1 py-0.2 rounded border border-border"
                      >
                        {ref}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <p className="text-xs md:text-sm text-text-1 leading-relaxed font-sans whitespace-pre-line">
                {section.body}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
