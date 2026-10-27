import React, { useState } from 'react';
import { Layers } from 'lucide-react';
import type { Finding, LanguageBreakdown } from '../../types/contract';
import { ArtifactCard } from '../artifacts/ArtifactCard';
import { EvidenceDrawer } from '../artifacts/EvidenceDrawer';

interface TechStackSectionProps {
  techStack: Finding[];
  configFiles: Finding[];
  languages: LanguageBreakdown[];
}

export const TechStackSection: React.FC<TechStackSectionProps> = ({
  techStack,
  configFiles,
  languages,
}) => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  // Calculate language bar colors
  const langColors = ['bg-cyan', 'bg-violet', 'bg-amber', 'bg-rust', 'bg-text-2'];

  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan" />
          <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider">
            Architecture & Tech Stack Excavation
          </h2>
        </div>
        <span className="font-mono text-xs text-text-2">
          {techStack.length + configFiles.length} detected findings
        </span>
      </div>

      {/* Languages Breakdown Bar */}
      {languages.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-text-2">
            <span>Language Distribution</span>
            <span>{languages.reduce((acc, l) => acc + l.bytes, 0).toLocaleString()} bytes</span>
          </div>

          {/* Stacked bar */}
          <div className="h-2 w-full bg-bg-2 rounded-full overflow-hidden flex">
            {languages.map((lang, idx) => (
              <div
                key={lang.name}
                style={{ width: `${Math.max(lang.percent, 1)}%` }}
                className={`${langColors[idx % langColors.length]} h-full transition-all`}
                title={`${lang.name}: ${lang.percent}%`}
              />
            ))}
          </div>

          {/* Language chips */}
          <div className="flex flex-wrap gap-3 pt-1 text-xs font-mono">
            {languages.map((lang, idx) => (
              <div key={lang.name} className="flex items-center gap-1.5 text-text-1">
                <span
                  className={`w-2 h-2 rounded-full ${langColors[idx % langColors.length]}`}
                />
                <span className="font-medium text-text-0">{lang.name}</span>
                <span className="text-text-2">{lang.percent}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Findings Grid */}
      <div className="space-y-4">
        {techStack.length === 0 && configFiles.length === 0 ? (
          <div className="p-6 text-center text-text-2 font-mono text-xs border border-dashed border-border rounded">
            No framework or tool manifests detected via deterministic rules.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {techStack.map((item) => (
              <ArtifactCard
                key={item.id}
                finding={item}
                onInspect={(f) => setSelectedFinding(f)}
              />
            ))}

            {configFiles.map((item) => (
              <ArtifactCard
                key={item.id}
                finding={item}
                onInspect={(f) => setSelectedFinding(f)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer
        isOpen={selectedFinding !== null}
        onClose={() => setSelectedFinding(null)}
        finding={selectedFinding}
      />
    </div>
  );
};
