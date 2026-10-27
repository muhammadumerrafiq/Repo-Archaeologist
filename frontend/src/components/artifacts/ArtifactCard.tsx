import React from 'react';
import { ChevronRight } from 'lucide-react';
import type { Finding } from '../../types/contract';
import { ProvenanceStamp } from '../ui/ProvenanceStamp';

interface ArtifactCardProps {
  finding: Finding;
  onInspect?: (finding: Finding) => void;
}

export const ArtifactCard: React.FC<ArtifactCardProps> = ({ finding, onInspect }) => {
  return (
    <div
      className="group flex flex-col sm:flex-row sm:items-center justify-between p-3.5 border-b border-line bg-bg-1 hover:bg-bg-2 transition-colors gap-3"
      id={finding.id}
    >
      <div className="flex items-start sm:items-center gap-3">
        <span className="font-mono text-xs text-text-2 bg-bg-0 border border-line px-1.5 py-0.5 rounded-[2px] shrink-0">
          {finding.id}
        </span>
        <div>
          <div className="flex items-center gap-2">
            <h4 className="font-mono text-sm font-medium text-text-0">{finding.label}</h4>
            <span className="text-[11px] font-mono text-text-2 uppercase">({finding.category})</span>
          </div>
          <p className="text-xs text-text-1 mt-0.5 line-clamp-1">{finding.summary}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
        <ProvenanceStamp confidence={finding.confidence} />
        {onInspect && (
          <button
            onClick={() => onInspect(finding)}
            aria-label={`View evidence for ${finding.label}`}
            className="flex items-center gap-1 font-mono text-xs text-text-2 hover:text-cyan border border-line px-2 py-1 rounded-[2px] transition-colors"
          >
            <span>Evidence ({finding.evidence.length})</span>
            <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        )}
      </div>
    </div>
  );
};
