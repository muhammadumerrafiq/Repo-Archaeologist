import React, { useState } from 'react';
import { Terminal } from 'lucide-react';
import type { Finding } from '../../types/contract';
import { ProvenanceStamp } from '../ui/ProvenanceStamp';
import { EvidenceDrawer } from '../artifacts/EvidenceDrawer';

interface EntryPointsSectionProps {
  entryPoints: Finding[];
}

export const EntryPointsSection: React.FC<EntryPointsSectionProps> = ({ entryPoints }) => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan" />
          <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider">
            Entry Point Candidates
          </h2>
        </div>
        <span className="font-mono text-xs text-text-2">
          {entryPoints.length} candidate{entryPoints.length === 1 ? '' : 's'} identified
        </span>
      </div>

      <p className="text-xs text-text-1 leading-relaxed">
        Candidate entry points detected via deterministic file path patterns, package manifests, or CLI binary definitions.
        Per analysis integrity rules, candidate entry points are prioritized for survey review rather than proven execution paths.
      </p>

      {entryPoints.length === 0 ? (
        <div className="p-6 text-center text-text-2 font-mono text-xs border border-dashed border-border rounded">
          No standard entry point candidates (main, index, app, server, CLI bin) identified in this repository.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {entryPoints.map((item) => (
            <div
              key={item.id}
              className="p-4 rounded bg-bg-2 border border-border flex flex-col justify-between gap-3 hover:border-cyan/40 transition-colors group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-text-2 bg-bg-0 px-1.5 py-0.5 rounded border border-border">
                      {item.id}
                    </span>
                    <span className="text-xs font-mono font-bold text-text-0 group-hover:text-cyan transition-colors truncate">
                      {item.label}
                    </span>
                  </div>
                  <ProvenanceStamp confidence={item.confidence} />
                </div>

                <p className="text-xs text-text-1 leading-relaxed font-sans">
                  {item.summary}
                </p>
              </div>

              <div className="pt-2 border-t border-border flex items-center justify-between text-xs font-mono text-text-2">
                <span className="text-[11px] uppercase tracking-wider text-cyan">
                  {item.category}
                </span>

                <button
                  type="button"
                  onClick={() => setSelectedFinding(item)}
                  className="text-text-1 hover:text-cyan transition-colors flex items-center gap-1 text-xs"
                >
                  <span>Evidence ({item.evidence.length})</span>
                  <span>&gt;</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer
        isOpen={selectedFinding !== null}
        onClose={() => setSelectedFinding(null)}
        finding={selectedFinding}
      />
    </div>
  );
};
