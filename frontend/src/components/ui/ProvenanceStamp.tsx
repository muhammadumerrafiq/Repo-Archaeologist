import React from 'react';
import type { Confidence } from '../../types/contract';

interface ProvenanceStampProps {
  confidence: Confidence;
  className?: string;
}

export const ProvenanceStamp: React.FC<ProvenanceStampProps> = ({ confidence, className = '' }) => {
  const isConfirmed = confidence === 'confirmed';

  return (
    <div
      role="status"
      title={
        isConfirmed
          ? 'Confirmed: Directly observable fact parsed from code or manifest.'
          : 'Heuristic: Inferred from standard naming conventions and heuristics.'
      }
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-mono tracking-wider uppercase font-semibold transition-colors cursor-help select-none ${
        isConfirmed
          ? 'border border-cyan text-cyan bg-cyan/5'
          : 'border border-dashed border-violet text-violet bg-violet/5'
      } ${className}`}
    >
      <span
        aria-hidden="true"
        className={`w-1.5 h-1.5 rounded-full ${
          isConfirmed ? 'bg-cyan' : 'border border-violet'
        }`}
      />
      <span>{confidence}</span>
    </div>
  );
};
